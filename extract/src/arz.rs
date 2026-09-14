//! ARZ database reader.
//!
//! An ARZ file is a table of records, each a zlib-compressed list of typed
//! variables, plus one shared string table that record names, variable names,
//! and string values all index into. Layout (all little-endian):
//!
//! ```text
//! header, 24 bytes
//!   0x00 i32  unknown
//!   0x04 u32  record table start      0x08 u32  record table size
//!   0x0C u32  record count            0x10 u32  string table start
//!   0x14 u32  string table size
//! record payloads follow the header; record offsets are relative to byte 24
//!
//! string table:  u32 count, then count × { u32 len, len bytes (cp1252) }
//! record table:  count × { u32 name index, u32 type len, type bytes,
//!                          u32 offset, u32 compressed size, 8 bytes skipped }
//! record payload (after zlib inflate):
//!   repeat { i16 type, i16 count, u32 name index, count × u32 value }
//!   type 0 = i32, 1 = f32 bit pattern, 2 = string table index, 3 = bool as i32
//! ```
//!
//! The two skipped bytes per record entry and the header's first word are
//! not needed to read the file; their meaning is unverified.

use std::collections::{HashMap, HashSet};
use std::fmt::Write as _;
use std::fs;
use std::io::Read;
use std::path::{Path, PathBuf};

use anyhow::{Context, Result, bail, ensure};
use flate2::read::ZlibDecoder;

use crate::Report;
use crate::cursor::{Cursor, decode_cp1252};

/// Size of the fixed header. Record offsets are relative to this.
pub const HEADER_LEN: usize = 24;

/// The fixed header at the start of the file.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct Header {
    pub unknown: i32,
    pub record_table_start: u32,
    pub record_table_size: u32,
    pub record_count: u32,
    pub string_table_start: u32,
    pub string_table_size: u32,
}

/// One entry of the record table: where a record is and what it is called.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct RecordInfo {
    /// Game path of the record, as stored, e.g. `records\item\foo.dbr`.
    pub name: String,
    /// Record class, e.g. `ItemBase`.
    pub record_type: String,
    /// Offset of the zlib stream, relative to the end of the header.
    pub offset: u32,
    pub compressed_size: u32,
}

/// A decoded record: an ordered list of typed variables.
#[derive(Debug, Clone, PartialEq)]
pub struct Record {
    pub name: String,
    pub record_type: String,
    pub variables: Vec<Variable>,
}

#[derive(Debug, Clone, PartialEq)]
pub struct Variable {
    pub name: String,
    pub value: Value,
}

/// Every variable is an array; single values are arrays of one.
#[derive(Debug, Clone, PartialEq)]
pub enum Value {
    Int(Vec<i32>),
    Float(Vec<f32>),
    Str(Vec<String>),
    Bool(Vec<bool>),
}

/// A parsed ARZ file. Holds the raw bytes so records can be decoded lazily.
pub struct ArzFile {
    data: Vec<u8>,
    header: Header,
    strings: Vec<String>,
    records: Vec<RecordInfo>,
}

impl std::fmt::Debug for ArzFile {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        f.debug_struct("ArzFile")
            .field("bytes", &self.data.len())
            .field("header", &self.header)
            .field("strings", &self.strings.len())
            .field("records", &self.records.len())
            .finish()
    }
}

impl ArzFile {
    /// Parse the header, string table, and record table. Record payloads are
    /// decoded on demand by [`ArzFile::read_record`].
    pub fn parse(data: Vec<u8>) -> Result<Self> {
        let header = parse_header(&data)?;
        let strings = parse_string_table(&data, &header)?;
        let records = parse_record_table(&data, &header, &strings)?;
        Ok(Self {
            data,
            header,
            strings,
            records,
        })
    }

    pub fn header(&self) -> &Header {
        &self.header
    }

    pub fn strings(&self) -> &[String] {
        &self.strings
    }

    pub fn records(&self) -> &[RecordInfo] {
        &self.records
    }

    /// Inflate and decode one record.
    pub fn read_record(&self, info: &RecordInfo) -> Result<Record> {
        let start = HEADER_LEN + info.offset as usize;
        let end = start + info.compressed_size as usize;
        ensure!(
            end <= self.data.len(),
            "record `{}` claims bytes {start}..{end} but the file is {} bytes",
            info.name,
            self.data.len()
        );

        let mut payload = Vec::new();
        ZlibDecoder::new(&self.data[start..end])
            .read_to_end(&mut payload)
            .with_context(|| format!("inflating record `{}`", info.name))?;

        let variables = parse_variables(&payload, &self.strings)
            .with_context(|| format!("decoding record `{}`", info.name))?;

        Ok(Record {
            name: info.name.clone(),
            record_type: info.record_type.clone(),
            variables,
        })
    }
}

impl Record {
    /// Render as DBR text: one `name,v1;v2;v3,` line per variable, in stored
    /// order. This is the format `tqdb/dbr.py` reads.
    pub fn to_dbr(&self) -> String {
        let mut out = String::new();
        for var in &self.variables {
            out.push_str(&var.name);
            out.push(',');
            match &var.value {
                Value::Int(v) => join(&mut out, v.iter(), |o, x| write!(o, "{x}")),
                Value::Float(v) => join(&mut out, v.iter(), |o, x| write!(o, "{x}")),
                Value::Str(v) => join(&mut out, v.iter(), |o, x| write!(o, "{x}")),
                Value::Bool(v) => join(&mut out, v.iter(), |o, x| write!(o, "{}", u8::from(*x))),
            }
            out.push_str(",\n");
        }
        out
    }
}

fn join<T>(
    out: &mut String,
    items: impl Iterator<Item = T>,
    mut fmt: impl FnMut(&mut String, T) -> std::fmt::Result,
) {
    for (i, item) in items.enumerate() {
        if i > 0 {
            out.push(';');
        }
        fmt(out, item).expect("writing to a String cannot fail");
    }
}

/// Filesystem path for a record, relative to the extraction root. Game paths
/// use backslashes and mixed case; on disk they are always forward-slash and
/// lowercase so lookups never depend on filesystem case sensitivity.
pub fn dbr_path(record_name: &str) -> PathBuf {
    PathBuf::from(record_name.replace('\\', "/").to_lowercase())
}

impl ArzFile {
    /// Write every record as a DBR file under `output`. `progress` is called
    /// with (done, total) every few thousand records.
    pub fn extract_all(&self, output: &Path, mut progress: impl FnMut(usize, usize)) -> Report {
        let total = self.records.len();
        let mut created_dirs: HashSet<PathBuf> = HashSet::new();
        let mut report = Report::default();

        for (i, info) in self.records.iter().enumerate() {
            let path = output.join(dbr_path(&info.name));
            let result = self.read_record(info).and_then(|record| {
                if let Some(parent) = path.parent()
                    && created_dirs.insert(parent.to_path_buf())
                {
                    fs::create_dir_all(parent)
                        .with_context(|| format!("creating {}", parent.display()))?;
                }
                let text = record.to_dbr();
                report.bytes += text.len() as u64;
                fs::write(&path, text).with_context(|| format!("writing {}", path.display()))
            });
            match result {
                Ok(()) => report.written += 1,
                Err(err) => report.fail(err),
            }
            if (i + 1) % 10_000 == 0 {
                progress(i + 1, total);
            }
        }
        report
    }
}

// --- parsing ---------------------------------------------------------------

fn parse_header(data: &[u8]) -> Result<Header> {
    ensure!(
        data.len() >= HEADER_LEN,
        "file is {} bytes, shorter than the {HEADER_LEN}-byte header",
        data.len()
    );
    let mut c = Cursor::new(data, 0);
    let header = Header {
        unknown: c.i32()?,
        record_table_start: c.u32()?,
        record_table_size: c.u32()?,
        record_count: c.u32()?,
        string_table_start: c.u32()?,
        string_table_size: c.u32()?,
    };

    let len = data.len() as u64;
    let rt_end = u64::from(header.record_table_start) + u64::from(header.record_table_size);
    let st_end = u64::from(header.string_table_start) + u64::from(header.string_table_size);
    ensure!(
        rt_end <= len,
        "record table ends at byte {rt_end}, past the end of the {len}-byte file"
    );
    ensure!(
        st_end <= len,
        "string table ends at byte {st_end}, past the end of the {len}-byte file"
    );
    Ok(header)
}

fn parse_string_table(data: &[u8], header: &Header) -> Result<Vec<String>> {
    let start = header.string_table_start as usize;
    let mut c = Cursor::new(data, start);
    let count = c.u32()? as usize;
    let mut strings = Vec::with_capacity(count);
    for i in 0..count {
        let len = c.u32()? as usize;
        let bytes = c
            .bytes(len)
            .with_context(|| format!("string {i} of {count}"))?;
        strings.push(decode_cp1252(bytes));
    }
    let consumed = c.pos - start;
    ensure!(
        consumed == header.string_table_size as usize,
        "string table: header says {} bytes, {count} strings occupy {consumed}",
        header.string_table_size
    );
    Ok(strings)
}

fn parse_record_table(data: &[u8], header: &Header, strings: &[String]) -> Result<Vec<RecordInfo>> {
    let start = header.record_table_start as usize;
    let mut c = Cursor::new(data, start);
    let count = header.record_count as usize;
    let mut records = Vec::with_capacity(count);
    for i in 0..count {
        let name_index = c.u32()? as usize;
        let type_len = c.u32()? as usize;
        let record_type = decode_cp1252(c.bytes(type_len)?);
        let offset = c.u32()?;
        let compressed_size = c.u32()?;
        c.bytes(8)?; // unverified: Grim Dawn stores a FILETIME here

        let name = strings
            .get(name_index)
            .with_context(|| {
                format!(
                    "record {i}: name index {name_index} outside string table of {}",
                    strings.len()
                )
            })?
            .clone();
        records.push(RecordInfo {
            name,
            record_type,
            offset,
            compressed_size,
        });
    }
    let consumed = c.pos - start;
    ensure!(
        consumed == header.record_table_size as usize,
        "record table: header says {} bytes, {count} entries occupy {consumed}",
        header.record_table_size
    );
    Ok(records)
}

fn parse_variables(payload: &[u8], strings: &[String]) -> Result<Vec<Variable>> {
    let mut c = Cursor::new(payload, 0);
    let mut variables = Vec::new();
    while c.remaining() > 0 {
        let type_id = c.i16()?;
        let count = c.i16()?;
        ensure!(count >= 1, "variable {} has count {count}", variables.len());
        let count = count as usize;
        let name_index = c.u32()? as usize;
        let name = strings
            .get(name_index)
            .with_context(|| {
                format!(
                    "variable {}: name index {name_index} outside string table",
                    variables.len()
                )
            })?
            .clone();

        let mut raw = Vec::with_capacity(count);
        for _ in 0..count {
            raw.push(c.u32()?);
        }

        let value = match type_id {
            0 => Value::Int(raw.into_iter().map(|x| x as i32).collect()),
            1 => Value::Float(raw.into_iter().map(f32::from_bits).collect()),
            2 => Value::Str(
                raw.into_iter()
                    .map(|idx| {
                        strings.get(idx as usize).cloned().with_context(|| {
                            format!("variable `{name}`: string index {idx} outside string table")
                        })
                    })
                    .collect::<Result<_>>()?,
            ),
            3 => Value::Bool(raw.into_iter().map(|x| x != 0).collect()),
            other => bail!("variable `{name}` has unknown type {other}"),
        };
        variables.push(Variable { name, value });
    }
    Ok(variables)
}

// --- diagnostics -----------------------------------------------------------

/// Human-readable summary for `tqextract arz info`, meant for checking a real
/// database.arz against this reader's understanding of the format.
pub fn describe(arz: &ArzFile) -> String {
    let h = arz.header();
    let mut out = String::new();
    let _ = writeln!(out, "header");
    let _ = writeln!(
        out,
        "  unknown word      {:#010x} ({})",
        h.unknown as u32, h.unknown
    );
    let _ = writeln!(
        out,
        "  record table      start {} size {}",
        h.record_table_start, h.record_table_size
    );
    let _ = writeln!(out, "  record count      {}", h.record_count);
    let _ = writeln!(
        out,
        "  string table      start {} size {}",
        h.string_table_start, h.string_table_size
    );
    let _ = writeln!(out, "strings             {}", arz.strings().len());
    let _ = writeln!(out, "records             {}", arz.records().len());

    let mut by_type: HashMap<&str, usize> = HashMap::new();
    for r in arz.records() {
        *by_type.entry(&r.record_type).or_default() += 1;
    }
    let mut types: Vec<_> = by_type.into_iter().collect();
    types.sort_by(|a, b| b.1.cmp(&a.1).then(a.0.cmp(b.0)));
    let _ = writeln!(out, "record types        {}", types.len());
    for (t, n) in types.iter().take(15) {
        let _ = writeln!(out, "  {n:>7}  {t}");
    }

    let _ = writeln!(out, "first records");
    for r in arz.records().iter().take(5) {
        let _ = writeln!(
            out,
            "  {}  ({} bytes)  {}",
            r.name, r.compressed_size, r.record_type
        );
    }
    out
}

// --- tests -----------------------------------------------------------------

#[cfg(test)]
pub(crate) mod test_support {
    //! A minimal ARZ writer, used only to round-trip the reader. It encodes the
    //! same layout the module doc describes; it is not a reference for the
    //! real format beyond that.

    use std::io::Write;

    use flate2::Compression;
    use flate2::write::ZlibEncoder;

    use super::{HEADER_LEN, Value};

    pub struct RecordSpec<'a> {
        pub name: &'a str,
        pub record_type: &'a str,
        pub variables: Vec<(&'a str, Value)>,
    }

    pub struct Builder {
        strings: Vec<Vec<u8>>,
    }

    impl Builder {
        pub fn new() -> Self {
            Self {
                strings: Vec::new(),
            }
        }

        fn intern(&mut self, s: &[u8]) -> u32 {
            if let Some(i) = self.strings.iter().position(|x| x == s) {
                return i as u32;
            }
            self.strings.push(s.to_vec());
            (self.strings.len() - 1) as u32
        }

        /// Build a file. `unknown` is the header's first word.
        pub fn build(mut self, unknown: i32, records: &[RecordSpec<'_>]) -> Vec<u8> {
            let mut payloads: Vec<u8> = Vec::new();
            let mut table: Vec<u8> = Vec::new();

            for rec in records {
                let name_idx = self.intern(rec.name.as_bytes());
                let mut raw = Vec::new();
                for (vname, value) in &rec.variables {
                    let vidx = self.intern(vname.as_bytes());
                    let (type_id, words): (i16, Vec<u32>) = match value {
                        Value::Int(v) => (0, v.iter().map(|x| *x as u32).collect()),
                        Value::Float(v) => (1, v.iter().map(|x| x.to_bits()).collect()),
                        Value::Str(v) => (
                            2,
                            v.iter()
                                .map(|s| self.intern(&encoding_rs::WINDOWS_1252.encode(s).0))
                                .collect(),
                        ),
                        Value::Bool(v) => (3, v.iter().map(|b| u32::from(*b)).collect()),
                    };
                    raw.extend_from_slice(&type_id.to_le_bytes());
                    raw.extend_from_slice(&(words.len() as i16).to_le_bytes());
                    raw.extend_from_slice(&vidx.to_le_bytes());
                    for w in words {
                        raw.extend_from_slice(&w.to_le_bytes());
                    }
                }
                let mut enc = ZlibEncoder::new(Vec::new(), Compression::default());
                enc.write_all(&raw).unwrap();
                let compressed = enc.finish().unwrap();

                let offset = payloads.len() as u32;
                payloads.extend_from_slice(&compressed);

                table.extend_from_slice(&name_idx.to_le_bytes());
                table.extend_from_slice(&(rec.record_type.len() as u32).to_le_bytes());
                table.extend_from_slice(rec.record_type.as_bytes());
                table.extend_from_slice(&offset.to_le_bytes());
                table.extend_from_slice(&(compressed.len() as u32).to_le_bytes());
                table.extend_from_slice(&[0u8; 8]);
            }

            let mut string_table = Vec::new();
            string_table.extend_from_slice(&(self.strings.len() as u32).to_le_bytes());
            for s in &self.strings {
                string_table.extend_from_slice(&(s.len() as u32).to_le_bytes());
                string_table.extend_from_slice(s);
            }

            let record_table_start = (HEADER_LEN + payloads.len()) as u32;
            let string_table_start = record_table_start + table.len() as u32;

            let mut file = Vec::new();
            file.extend_from_slice(&unknown.to_le_bytes());
            file.extend_from_slice(&record_table_start.to_le_bytes());
            file.extend_from_slice(&(table.len() as u32).to_le_bytes());
            file.extend_from_slice(&(records.len() as u32).to_le_bytes());
            file.extend_from_slice(&string_table_start.to_le_bytes());
            file.extend_from_slice(&(string_table.len() as u32).to_le_bytes());
            file.extend_from_slice(&payloads);
            file.extend_from_slice(&table);
            file.extend_from_slice(&string_table);
            file
        }

        /// Intern a raw byte string (for testing cp1252 decoding).
        pub fn intern_raw(&mut self, bytes: &[u8]) -> u32 {
            self.intern(bytes)
        }
    }
}

#[cfg(test)]
mod tests {
    use super::test_support::{Builder, RecordSpec};
    use super::*;

    fn sample() -> Vec<u8> {
        Builder::new().build(
            0x0003_0002,
            &[
                RecordSpec {
                    name: r"Records\Item\EquipmentWeapon\Sword\Sword_01.dbr",
                    record_type: "WeaponMelee_Sword",
                    variables: vec![
                        (
                            "templateName",
                            Value::Str(vec![r"database\Templates\WeaponMelee_Sword.tpl".into()]),
                        ),
                        ("Class", Value::Str(vec!["WeaponMelee_Sword".into()])),
                        ("itemLevel", Value::Int(vec![20])),
                        (
                            "offensivePhysicalMin",
                            Value::Float(vec![12.0, 14.5, 16.25]),
                        ),
                        ("cannotPickUpMultiple", Value::Bool(vec![true])),
                        ("itemCostScalePercent", Value::Float(vec![0.1])),
                    ],
                },
                RecordSpec {
                    name: r"records\game\itemcost.dbr",
                    record_type: "ItemCost",
                    variables: vec![("levels", Value::Int(vec![1, 2, 3]))],
                },
            ],
        )
    }

    #[test]
    fn parses_header_and_tables() {
        let arz = ArzFile::parse(sample()).unwrap();
        assert_eq!(arz.header().unknown, 0x0003_0002);
        assert_eq!(arz.header().record_count, 2);
        assert_eq!(arz.records().len(), 2);
        assert_eq!(arz.records()[0].record_type, "WeaponMelee_Sword");
        assert_eq!(arz.records()[1].name, r"records\game\itemcost.dbr");
        assert_eq!(arz.records()[0].offset, 0);
        assert!(arz.strings().iter().any(|s| s == "itemLevel"));
    }

    #[test]
    fn round_trips_every_value_type() {
        let arz = ArzFile::parse(sample()).unwrap();
        let rec = arz.read_record(&arz.records()[0]).unwrap();
        assert_eq!(rec.variables.len(), 6);
        assert_eq!(rec.variables[2].name, "itemLevel");
        assert_eq!(rec.variables[2].value, Value::Int(vec![20]));
        assert_eq!(
            rec.variables[3].value,
            Value::Float(vec![12.0, 14.5, 16.25])
        );
        assert_eq!(rec.variables[4].value, Value::Bool(vec![true]));
        assert_eq!(
            rec.variables[0].value,
            Value::Str(vec![r"database\Templates\WeaponMelee_Sword.tpl".into()])
        );

        let rec2 = arz.read_record(&arz.records()[1]).unwrap();
        assert_eq!(rec2.variables[0].value, Value::Int(vec![1, 2, 3]));
    }

    #[test]
    fn renders_dbr_text() {
        let arz = ArzFile::parse(sample()).unwrap();
        let rec = arz.read_record(&arz.records()[0]).unwrap();
        let expected = "templateName,database\\Templates\\WeaponMelee_Sword.tpl,\n\
                        Class,WeaponMelee_Sword,\n\
                        itemLevel,20,\n\
                        offensivePhysicalMin,12;14.5;16.25,\n\
                        cannotPickUpMultiple,1,\n\
                        itemCostScalePercent,0.1,\n";
        assert_eq!(rec.to_dbr(), expected);
    }

    #[test]
    fn dbr_path_is_forward_slash_lowercase() {
        assert_eq!(
            dbr_path(r"Records\Item\EquipmentWeapon\Sword\Sword_01.dbr"),
            PathBuf::from("records/item/equipmentweapon/sword/sword_01.dbr")
        );
    }

    #[test]
    fn decodes_cp1252_strings() {
        let mut b = Builder::new();
        // "caf\xe9" in cp1252 is "café"; 0x80 is the euro sign, which Latin-1 lacks.
        let idx = b.intern_raw(b"caf\xe9 \x80");
        let file = b.build(
            0,
            &[RecordSpec {
                name: "r.dbr",
                record_type: "T",
                variables: vec![("description", Value::Str(vec!["caf\u{e9} \u{20ac}".into()]))],
            }],
        );
        let arz = ArzFile::parse(file).unwrap();
        assert_eq!(arz.strings()[idx as usize], "café €");
        let rec = arz.read_record(&arz.records()[0]).unwrap();
        assert_eq!(rec.variables[0].value, Value::Str(vec!["café €".into()]));
    }

    #[test]
    fn rejects_truncated_file() {
        let file = sample();
        let err = ArzFile::parse(file[..file.len() - 10].to_vec()).unwrap_err();
        assert!(err.to_string().contains("past the end"), "{err}");
    }

    #[test]
    fn rejects_too_short_header() {
        let err = ArzFile::parse(vec![0; 10]).unwrap_err();
        assert!(err.to_string().contains("shorter than"), "{err}");
    }

    #[test]
    fn rejects_record_table_size_mismatch() {
        let mut file = sample();
        // Corrupt the header's record table size (bytes 8..12).
        let wrong = (u32::from_le_bytes(file[8..12].try_into().unwrap()) + 4).to_le_bytes();
        file[8..12].copy_from_slice(&wrong);
        let err = ArzFile::parse(file).unwrap_err();
        assert!(err.to_string().contains("record table"), "{err}");
    }

    #[test]
    fn rejects_corrupt_payload() {
        let mut file = sample();
        // First record payload starts right after the header; break the zlib header.
        file[HEADER_LEN] ^= 0xff;
        let arz = ArzFile::parse(file).unwrap();
        let err = arz.read_record(&arz.records()[0]).unwrap_err();
        assert!(err.to_string().contains("inflating"), "{err}");
    }

    #[test]
    fn describe_mentions_counts_and_types() {
        let arz = ArzFile::parse(sample()).unwrap();
        let text = describe(&arz);
        assert!(text.contains("records             2"));
        assert!(text.contains("WeaponMelee_Sword"));
    }
}
