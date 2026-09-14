//! ARC archive reader.
//!
//! An ARC file is a flat archive: a list of named entries, each stored either
//! raw or as a sequence of independently zlib-compressed parts. Layout (all
//! little-endian; verified on the Anniversary Edition's `Templates.arc` and
//! `Text_EN.arc`, where every table adds up to the file length exactly):
//!
//! ```text
//! header, 28 bytes
//!   0x00 "ARC\0"               0x04 u32 version (1 in TQ AE; Grim Dawn uses 3)
//!   0x08 u32 entry count      0x0C u32 part count
//!   0x10 u32 part table size (= part count × 12)
//!   0x14 u32 string table size
//!   0x18 u32 toc offset
//! entry payloads follow the header
//!
//! at toc offset:      part count × { u32 offset, u32 compressed size, u32 real size }
//! then:               string table (entry names, addressed by offset and length)
//! then, to the end:   entry count × 44 bytes {
//!                       u32 storage (1 = stored, 3 = compressed)
//!                       u32 offset, u32 compressed size, u32 real size
//!                       u32 adler32 of the decompressed data
//!                       u64 filetime
//!                       u32 part count, u32 first part index
//!                       u32 name length, u32 name offset (into the string table)
//!                     }
//! ```
//!
//! A compressed entry is the concatenation of its parts, each a zlib stream.
//! A part whose compressed and real sizes are equal is stored raw. Entries
//! with an empty name are deleted.

use std::collections::HashMap;
use std::fmt::Write as _;
use std::io::Read;
use std::path::PathBuf;

use anyhow::{Context, Result, bail, ensure};
use flate2::read::ZlibDecoder;

use crate::cursor::{Cursor, decode_cp1252};

pub const HEADER_LEN: usize = 28;
pub const PART_LEN: usize = 12;
pub const ENTRY_LEN: usize = 44;
const MAGIC: &[u8; 4] = b"ARC\0";

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct Header {
    pub version: u32,
    pub entry_count: u32,
    pub part_count: u32,
    pub part_table_size: u32,
    pub string_table_size: u32,
    pub toc_offset: u32,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct Part {
    pub offset: u32,
    pub compressed_size: u32,
    pub real_size: u32,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum Storage {
    Stored,
    Compressed,
    Unknown(u32),
}

impl Storage {
    fn from_raw(raw: u32) -> Self {
        match raw {
            1 => Storage::Stored,
            3 => Storage::Compressed,
            other => Storage::Unknown(other),
        }
    }
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Entry {
    /// Name as stored, e.g. `templates\templatebase\itembase.tpl`.
    pub name: String,
    pub storage: Storage,
    pub offset: u32,
    pub compressed_size: u32,
    pub real_size: u32,
    pub adler32: u32,
    pub filetime: u64,
    pub first_part: u32,
    pub part_count: u32,
}

/// A parsed ARC file. Holds the raw bytes so entries can be read lazily.
pub struct ArcFile {
    data: Vec<u8>,
    header: Header,
    parts: Vec<Part>,
    entries: Vec<Entry>,
    deleted: usize,
}

impl std::fmt::Debug for ArcFile {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        f.debug_struct("ArcFile")
            .field("bytes", &self.data.len())
            .field("header", &self.header)
            .field("parts", &self.parts.len())
            .field("entries", &self.entries.len())
            .field("deleted", &self.deleted)
            .finish()
    }
}

impl ArcFile {
    /// Parse the header, part table, string table, and entry table. Payloads
    /// are read on demand by [`ArcFile::read_entry`].
    pub fn parse(data: Vec<u8>) -> Result<Self> {
        let header = parse_header(&data)?;
        let parts = parse_parts(&data, &header)?;
        let (entries, deleted) = parse_entries(&data, &header)?;
        Ok(Self {
            data,
            header,
            parts,
            entries,
            deleted,
        })
    }

    pub fn header(&self) -> &Header {
        &self.header
    }

    pub fn parts(&self) -> &[Part] {
        &self.parts
    }

    /// Live entries, in stored order. Deleted entries (empty name) are not included.
    pub fn entries(&self) -> &[Entry] {
        &self.entries
    }

    /// Number of deleted entries skipped while parsing.
    pub fn deleted(&self) -> usize {
        self.deleted
    }

    /// Decompress one entry and verify its length and adler32 checksum.
    pub fn read_entry(&self, entry: &Entry) -> Result<Vec<u8>> {
        let data = match entry.storage {
            Storage::Stored => {
                let start = entry.offset as usize;
                let end = start + entry.real_size as usize;
                ensure!(
                    end <= self.data.len(),
                    "entry `{}` claims bytes {start}..{end} but the file is {} bytes",
                    entry.name,
                    self.data.len()
                );
                self.data[start..end].to_vec()
            }
            Storage::Compressed => {
                let first = entry.first_part as usize;
                let last = first + entry.part_count as usize;
                ensure!(
                    last <= self.parts.len(),
                    "entry `{}` uses parts {first}..{last} but there are {}",
                    entry.name,
                    self.parts.len()
                );
                let mut out = Vec::with_capacity(entry.real_size as usize);
                for (i, part) in self.parts[first..last].iter().enumerate() {
                    self.read_part(part, &mut out).with_context(|| {
                        format!("entry `{}`, part {i} of {}", entry.name, entry.part_count)
                    })?;
                }
                out
            }
            Storage::Unknown(raw) => bail!("entry `{}` has unknown storage type {raw}", entry.name),
        };

        ensure!(
            data.len() == entry.real_size as usize,
            "entry `{}`: expected {} bytes, got {}",
            entry.name,
            entry.real_size,
            data.len()
        );
        let checksum = adler32(&data);
        ensure!(
            checksum == entry.adler32,
            "entry `{}`: adler32 {checksum:#010x} does not match stored {:#010x}",
            entry.name,
            entry.adler32
        );
        Ok(data)
    }

    fn read_part(&self, part: &Part, out: &mut Vec<u8>) -> Result<()> {
        let start = part.offset as usize;
        let end = start + part.compressed_size as usize;
        ensure!(
            end <= self.data.len(),
            "part claims bytes {start}..{end} but the file is {} bytes",
            self.data.len()
        );
        let raw = &self.data[start..end];
        let before = out.len();
        if part.compressed_size == part.real_size {
            out.extend_from_slice(raw);
        } else {
            ZlibDecoder::new(raw)
                .read_to_end(out)
                .context("inflating")?;
        }
        let got = out.len() - before;
        ensure!(
            got == part.real_size as usize,
            "part inflated to {got} bytes, expected {}",
            part.real_size
        );
        Ok(())
    }
}

/// Filesystem path for an entry, relative to the extraction root: forward
/// slashes and lowercase, like [`crate::arz::dbr_path`].
pub fn entry_path(name: &str) -> PathBuf {
    PathBuf::from(name.replace('\\', "/").to_lowercase())
}

/// Adler-32 as used by zlib, computed over the decompressed entry.
pub fn adler32(data: &[u8]) -> u32 {
    const MOD: u32 = 65_521;
    let mut a: u32 = 1;
    let mut b: u32 = 0;
    // Process in chunks small enough that the sums cannot overflow u32.
    for chunk in data.chunks(5_552) {
        for &byte in chunk {
            a += u32::from(byte);
            b += a;
        }
        a %= MOD;
        b %= MOD;
    }
    (b << 16) | a
}

// --- parsing ---------------------------------------------------------------

fn parse_header(data: &[u8]) -> Result<Header> {
    ensure!(
        data.len() >= HEADER_LEN,
        "file is {} bytes, shorter than the {HEADER_LEN}-byte header",
        data.len()
    );
    ensure!(
        &data[..4] == MAGIC,
        "not an ARC file: magic is {:?}, expected {:?}",
        &data[..4],
        MAGIC
    );
    let mut c = Cursor::new(data, 4);
    let header = Header {
        version: c.u32()?,
        entry_count: c.u32()?,
        part_count: c.u32()?,
        part_table_size: c.u32()?,
        string_table_size: c.u32()?,
        toc_offset: c.u32()?,
    };

    ensure!(
        header.part_table_size as usize == header.part_count as usize * PART_LEN,
        "part table size {} does not equal {} parts × {PART_LEN}",
        header.part_table_size,
        header.part_count
    );
    let expected_len = header.toc_offset as u64
        + u64::from(header.part_table_size)
        + u64::from(header.string_table_size)
        + u64::from(header.entry_count) * ENTRY_LEN as u64;
    ensure!(
        expected_len == data.len() as u64,
        "toc + tables + {} entries end at byte {expected_len}, but the file is {} bytes",
        header.entry_count,
        data.len()
    );
    Ok(header)
}

fn parse_parts(data: &[u8], header: &Header) -> Result<Vec<Part>> {
    let mut c = Cursor::new(data, header.toc_offset as usize);
    let mut parts = Vec::with_capacity(header.part_count as usize);
    for _ in 0..header.part_count {
        parts.push(Part {
            offset: c.u32()?,
            compressed_size: c.u32()?,
            real_size: c.u32()?,
        });
    }
    Ok(parts)
}

fn parse_entries(data: &[u8], header: &Header) -> Result<(Vec<Entry>, usize)> {
    let strings_start = header.toc_offset as usize + header.part_table_size as usize;
    let strings_end = strings_start + header.string_table_size as usize;
    let strings = &data[strings_start..strings_end];

    let mut c = Cursor::new(data, strings_end);
    let mut entries = Vec::with_capacity(header.entry_count as usize);
    let mut deleted = 0;
    for i in 0..header.entry_count {
        let storage = Storage::from_raw(c.u32()?);
        let offset = c.u32()?;
        let compressed_size = c.u32()?;
        let real_size = c.u32()?;
        let adler32 = c.u32()?;
        let filetime = c.u64()?;
        let part_count = c.u32()?;
        let first_part = c.u32()?;
        let name_len = c.u32()? as usize;
        let name_offset = c.u32()? as usize;

        ensure!(
            name_offset + name_len <= strings.len(),
            "entry {i}: name at {name_offset}+{name_len} is outside the {}-byte string table",
            strings.len()
        );
        let raw_name = &strings[name_offset..name_offset + name_len];
        let raw_name = raw_name.strip_suffix(&[0]).unwrap_or(raw_name);
        if raw_name.is_empty() {
            deleted += 1;
            continue;
        }
        entries.push(Entry {
            name: decode_cp1252(raw_name),
            storage,
            offset,
            compressed_size,
            real_size,
            adler32,
            filetime,
            first_part,
            part_count,
        });
    }
    Ok((entries, deleted))
}

// --- diagnostics -----------------------------------------------------------

/// Human-readable summary for `tqextract arc info`.
pub fn describe(arc: &ArcFile) -> String {
    let h = arc.header();
    let mut out = String::new();
    let _ = writeln!(out, "header");
    let _ = writeln!(out, "  version           {}", h.version);
    let _ = writeln!(out, "  entries           {}", h.entry_count);
    let _ = writeln!(out, "  parts             {}", h.part_count);
    let _ = writeln!(out, "  string table      {} bytes", h.string_table_size);
    let _ = writeln!(out, "  toc offset        {}", h.toc_offset);
    let _ = writeln!(out, "live entries        {}", arc.entries().len());
    let _ = writeln!(out, "deleted entries     {}", arc.deleted());

    let mut by_storage: HashMap<String, usize> = HashMap::new();
    let mut by_ext: HashMap<String, usize> = HashMap::new();
    let mut total_real: u64 = 0;
    for e in arc.entries() {
        *by_storage.entry(format!("{:?}", e.storage)).or_default() += 1;
        let ext = e.name.rsplit('.').next().unwrap_or("").to_lowercase();
        *by_ext.entry(ext).or_default() += 1;
        total_real += u64::from(e.real_size);
    }
    let _ = writeln!(out, "uncompressed total  {total_real} bytes");
    let _ = writeln!(out, "storage");
    let mut storage: Vec<_> = by_storage.into_iter().collect();
    storage.sort();
    for (s, n) in storage {
        let _ = writeln!(out, "  {n:>7}  {s}");
    }
    let _ = writeln!(out, "extensions");
    let mut exts: Vec<_> = by_ext.into_iter().collect();
    exts.sort_by(|a, b| b.1.cmp(&a.1).then(a.0.cmp(&b.0)));
    for (ext, n) in exts.iter().take(10) {
        let _ = writeln!(out, "  {n:>7}  .{ext}");
    }
    let _ = writeln!(out, "first entries");
    for e in arc.entries().iter().take(8) {
        let _ = writeln!(
            out,
            "  {}  ({} -> {} bytes, {} part(s))",
            e.name, e.compressed_size, e.real_size, e.part_count
        );
    }
    out
}

// --- tests -----------------------------------------------------------------

#[cfg(test)]
pub(crate) mod test_support {
    //! A minimal ARC writer for round-trip tests. Same caveat as the ARZ one:
    //! it encodes the layout in the module doc, nothing more.

    use std::io::Write;

    use flate2::Compression;
    use flate2::write::ZlibEncoder;

    use super::{ENTRY_LEN, HEADER_LEN, PART_LEN, adler32};

    pub struct FileSpec<'a> {
        pub name: &'a str,
        pub data: &'a [u8],
        /// `None` stores raw; `Some(n)` compresses in `n` parts.
        pub parts: Option<usize>,
    }

    pub fn build(version: u32, files: &[FileSpec<'_>], deleted_entries: usize) -> Vec<u8> {
        let mut payload: Vec<u8> = Vec::new();
        let mut parts: Vec<(u32, u32, u32)> = Vec::new();
        let mut strings: Vec<u8> = Vec::new();
        let mut entries: Vec<u8> = Vec::new();

        let push_entry = |entries: &mut Vec<u8>,
                          storage: u32,
                          offset: u32,
                          csize: u32,
                          rsize: u32,
                          sum: u32,
                          part_count: u32,
                          first_part: u32,
                          name_len: u32,
                          name_off: u32| {
            for v in [storage, offset, csize, rsize, sum] {
                entries.extend_from_slice(&v.to_le_bytes());
            }
            entries.extend_from_slice(&0x01d0_0000_0000_0000u64.to_le_bytes());
            for v in [part_count, first_part, name_len, name_off] {
                entries.extend_from_slice(&v.to_le_bytes());
            }
        };

        for f in files {
            let name_off = strings.len() as u32;
            strings.extend_from_slice(f.name.as_bytes());
            strings.push(0);
            let name_len = (f.name.len() + 1) as u32;
            let sum = adler32(f.data);

            match f.parts {
                None => {
                    let offset = (HEADER_LEN + payload.len()) as u32;
                    payload.extend_from_slice(f.data);
                    let first = parts.len() as u32;
                    parts.push((offset, f.data.len() as u32, f.data.len() as u32));
                    push_entry(
                        &mut entries,
                        1,
                        offset,
                        f.data.len() as u32,
                        f.data.len() as u32,
                        sum,
                        1,
                        first,
                        name_len,
                        name_off,
                    );
                }
                Some(n) => {
                    let first = parts.len() as u32;
                    let entry_offset = (HEADER_LEN + payload.len()) as u32;
                    let chunk = f.data.len().div_ceil(n).max(1);
                    let mut total_c = 0u32;
                    for piece in f.data.chunks(chunk) {
                        let mut enc = ZlibEncoder::new(Vec::new(), Compression::default());
                        enc.write_all(piece).unwrap();
                        let c = enc.finish().unwrap();
                        let offset = (HEADER_LEN + payload.len()) as u32;
                        payload.extend_from_slice(&c);
                        parts.push((offset, c.len() as u32, piece.len() as u32));
                        total_c += c.len() as u32;
                    }
                    let count = parts.len() as u32 - first;
                    push_entry(
                        &mut entries,
                        3,
                        entry_offset,
                        total_c,
                        f.data.len() as u32,
                        sum,
                        count,
                        first,
                        name_len,
                        name_off,
                    );
                }
            }
        }
        for _ in 0..deleted_entries {
            push_entry(&mut entries, 3, 0, 0, 0, 0, 0, 0, 0, 0);
        }

        let toc_offset = (HEADER_LEN + payload.len()) as u32;
        let mut part_table = Vec::new();
        for (o, c, r) in &parts {
            for v in [o, c, r] {
                part_table.extend_from_slice(&v.to_le_bytes());
            }
        }
        assert_eq!(part_table.len(), parts.len() * PART_LEN);
        let entry_count = (files.len() + deleted_entries) as u32;
        assert_eq!(entries.len(), entry_count as usize * ENTRY_LEN);

        let mut file = Vec::new();
        file.extend_from_slice(b"ARC\0");
        for v in [
            version,
            entry_count,
            parts.len() as u32,
            part_table.len() as u32,
            strings.len() as u32,
            toc_offset,
        ] {
            file.extend_from_slice(&v.to_le_bytes());
        }
        file.extend_from_slice(&payload);
        file.extend_from_slice(&part_table);
        file.extend_from_slice(&strings);
        file.extend_from_slice(&entries);
        file
    }
}

#[cfg(test)]
mod tests {
    use super::test_support::{FileSpec, build};
    use super::*;

    fn big() -> Vec<u8> {
        (0..20_000u32)
            .flat_map(|i| (i % 251).to_le_bytes())
            .collect()
    }

    fn sample() -> (Vec<u8>, Vec<u8>) {
        let big = big();
        let file = build(
            1,
            &[
                FileSpec {
                    name: r"templates\templatebase\itembase.tpl",
                    data: b"Group\n{\n  name = \"Header\"\n}\n",
                    parts: Some(1),
                },
                FileSpec {
                    name: "readme.txt",
                    data: b"stored raw",
                    parts: None,
                },
                FileSpec {
                    name: r"Templates\Monster.tpl",
                    data: &big,
                    parts: Some(4),
                },
            ],
            1,
        );
        (file, big)
    }

    #[test]
    fn parses_header_and_tables() {
        let (file, _) = sample();
        let arc = ArcFile::parse(file).unwrap();
        assert_eq!(arc.header().version, 1);
        assert_eq!(arc.header().entry_count, 4);
        assert_eq!(arc.entries().len(), 3);
        assert_eq!(arc.deleted(), 1);
        assert_eq!(arc.parts().len(), 6);
        assert_eq!(
            arc.entries()[0].name,
            r"templates\templatebase\itembase.tpl"
        );
        assert_eq!(arc.entries()[1].storage, Storage::Stored);
        assert_eq!(arc.entries()[2].part_count, 4);
    }

    #[test]
    fn round_trips_stored_and_multipart_entries() {
        let (file, big) = sample();
        let arc = ArcFile::parse(file).unwrap();
        assert_eq!(
            arc.read_entry(&arc.entries()[0]).unwrap(),
            b"Group\n{\n  name = \"Header\"\n}\n"
        );
        assert_eq!(arc.read_entry(&arc.entries()[1]).unwrap(), b"stored raw");
        assert_eq!(arc.read_entry(&arc.entries()[2]).unwrap(), big);
    }

    #[test]
    fn entry_path_is_forward_slash_lowercase() {
        assert_eq!(
            entry_path(r"Templates\TemplateBase\ItemBase.tpl"),
            PathBuf::from("templates/templatebase/itembase.tpl")
        );
    }

    #[test]
    fn adler32_matches_reference_values() {
        // Reference values from the zlib specification and common test vectors.
        assert_eq!(adler32(b""), 0x0000_0001);
        assert_eq!(adler32(b"Wikipedia"), 0x11E6_0398);
        assert_eq!(adler32(&big()), adler32(&big()));
    }

    #[test]
    fn detects_checksum_mismatch() {
        let (mut file, _) = sample();
        // Entries are the last 4 × 44 bytes; the adler32 is the fifth u32 of the first entry.
        let entries_start = file.len() - 4 * ENTRY_LEN;
        let pos = entries_start + 16;
        file[pos] ^= 0xff;
        let arc = ArcFile::parse(file).unwrap();
        let err = arc.read_entry(&arc.entries()[0]).unwrap_err();
        assert!(err.to_string().contains("adler32"), "{err}");
    }

    #[test]
    fn rejects_bad_magic() {
        let (mut file, _) = sample();
        file[0] = b'X';
        let err = ArcFile::parse(file).unwrap_err();
        assert!(err.to_string().contains("not an ARC file"), "{err}");
    }

    #[test]
    fn rejects_truncated_file() {
        let (file, _) = sample();
        let err = ArcFile::parse(file[..file.len() - 1].to_vec()).unwrap_err();
        assert!(err.to_string().contains("end at byte"), "{err}");
    }

    #[test]
    fn describe_mentions_counts() {
        let (file, _) = sample();
        let arc = ArcFile::parse(file).unwrap();
        let text = describe(&arc);
        assert!(text.contains("live entries        3"));
        assert!(text.contains("deleted entries     1"));
        assert!(text.contains(".tpl"));
    }
}
