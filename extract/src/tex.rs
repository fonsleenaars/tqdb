//! TEX texture reader: a small wrapper around a DirectDraw Surface with two
//! quirks. Layout (little-endian; verified on Anniversary Edition item icons,
//! both header versions):
//!
//! ```text
//! v1:  "TEX\x01"  u32 unknown (0)  u32 dds length          DDS at byte 12
//! v2:  "TEX\x02"  u32 unknown (0)  u8 flag  u32 dds length  DDS at byte 13
//!
//! DDS: magic "DDS " or "DDSR", then the standard 124-byte header
//!   +0 size 124   +4 flags   +8 height   +12 width   +16 pitch   +20 depth
//!   +24 mip count   +28 reserved[11]
//!   +72 pixel format { size 32, flags, fourcc, bit count, r/g/b/a masks }
//!   +104 caps[4]   +120 reserved
//! surfaces follow at DDS byte 128
//! ```
//!
//! Quirks: `DDSR` means the mip chain is stored smallest first, so the full
//! size surface is the *last* one. Uncompressed surfaces carry zeroed RGB
//! masks and no alpha flag; they are A8R8G8B8 (bytes B, G, R, A).
//! Pixel formats seen: DXT1, DXT3, DXT5, uncompressed 32-bit and 24-bit.

use std::fmt::Write as _;
use std::fs;
use std::io::Cursor as IoCursor;
use std::path::{Path, PathBuf};

use anyhow::{Context, Result, bail, ensure};

use crate::Report;
use crate::cursor::Cursor;

const DDS_HEADER_LEN: usize = 128;
const DDPF_FOURCC: u32 = 0x4;

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum PixelFormat {
    Dxt1,
    Dxt3,
    Dxt5,
    /// Uncompressed, `bits` per pixel, bytes in B, G, R, (A) order.
    Bgra {
        bits: u32,
    },
}

impl PixelFormat {
    /// Bytes of one surface at the given dimensions.
    pub fn surface_size(self, width: u32, height: u32) -> usize {
        match self {
            PixelFormat::Dxt1 => blocks(width) * blocks(height) * 8,
            PixelFormat::Dxt3 | PixelFormat::Dxt5 => blocks(width) * blocks(height) * 16,
            PixelFormat::Bgra { bits } => width as usize * height as usize * (bits as usize / 8),
        }
    }
}

fn blocks(dim: u32) -> usize {
    dim.div_ceil(4).max(1) as usize
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct TexFile<'a> {
    pub version: u8,
    pub unknown: u32,
    /// Only present in v2 headers.
    pub flag: Option<u8>,
    pub dds_len: u32,
    /// Bytes after the declared DDS payload; zero for single-frame textures.
    pub trailing: usize,
    pub reversed_mips: bool,
    pub width: u32,
    pub height: u32,
    pub mip_count: u32,
    pub format: PixelFormat,
    pub fourcc: [u8; 4],
    pub masks: [u32; 4],
    surfaces: &'a [u8],
}

impl<'a> TexFile<'a> {
    pub fn parse(data: &'a [u8]) -> Result<Self> {
        ensure!(data.len() >= 4 && &data[..3] == b"TEX", "not a TEX file");
        let version = data[3];
        let mut c = Cursor::new(data, 4);
        let unknown = c.u32()?;
        let flag = match version {
            1 => None,
            2 => Some(c.bytes(1)?[0]),
            other => bail!("unsupported TEX version {other}"),
        };
        let dds_len = c.u32()?;
        let dds_start = c.pos;
        ensure!(
            dds_start + dds_len as usize <= data.len(),
            "TEX declares {dds_len} DDS bytes at {dds_start} but the file is {} bytes",
            data.len()
        );
        let dds = &data[dds_start..dds_start + dds_len as usize];
        let trailing = data.len() - dds_start - dds_len as usize;

        ensure!(
            dds.len() >= DDS_HEADER_LEN,
            "DDS payload is only {} bytes",
            dds.len()
        );
        let reversed_mips = match &dds[..4] {
            b"DDS " => false,
            b"DDSR" => true,
            other => bail!("unknown DDS magic {other:?}"),
        };
        let mut d = Cursor::new(dds, 4);
        let size = d.u32()?;
        ensure!(size == 124, "DDS header size is {size}, expected 124");
        let _flags = d.u32()?;
        let height = d.u32()?;
        let width = d.u32()?;
        let _pitch = d.u32()?;
        let _depth = d.u32()?;
        let mip_count = d.u32()?.max(1);
        d.bytes(44)?; // reserved[11]
        let pf_size = d.u32()?;
        ensure!(
            pf_size == 32,
            "DDS pixel format size is {pf_size}, expected 32"
        );
        let pf_flags = d.u32()?;
        let fourcc: [u8; 4] = d.bytes(4)?.try_into().unwrap();
        let bits = d.u32()?;
        let masks = [d.u32()?, d.u32()?, d.u32()?, d.u32()?];

        let format = if pf_flags & DDPF_FOURCC != 0 {
            match &fourcc {
                b"DXT1" => PixelFormat::Dxt1,
                b"DXT3" => PixelFormat::Dxt3,
                b"DXT5" => PixelFormat::Dxt5,
                other => bail!("unsupported fourcc {:?}", String::from_utf8_lossy(other)),
            }
        } else {
            ensure!(
                bits == 32 || bits == 24,
                "unsupported uncompressed bit depth {bits}"
            );
            PixelFormat::Bgra { bits }
        };
        ensure!(width > 0 && height > 0, "texture is {width}x{height}");

        Ok(Self {
            version,
            unknown,
            flag,
            dds_len,
            trailing,
            reversed_mips,
            width,
            height,
            mip_count,
            format,
            fourcc,
            masks,
            surfaces: &dds[DDS_HEADER_LEN..],
        })
    }

    /// Total bytes of the full mip chain as declared by the header.
    pub fn expected_chain_size(&self) -> usize {
        (0..self.mip_count)
            .map(|i| {
                let w = (self.width >> i).max(1);
                let h = (self.height >> i).max(1);
                self.format.surface_size(w, h)
            })
            .sum()
    }

    /// Bytes actually present after the DDS header.
    pub fn surfaces_len(&self) -> usize {
        self.surfaces.len()
    }

    /// The full-resolution surface, wherever the file put it.
    pub fn top_surface(&self) -> Result<&'a [u8]> {
        let size = self.format.surface_size(self.width, self.height);
        ensure!(
            self.surfaces.len() >= size,
            "top surface needs {size} bytes but only {} follow the header",
            self.surfaces.len()
        );
        Ok(if self.reversed_mips && self.mip_count > 1 {
            &self.surfaces[self.surfaces.len() - size..]
        } else {
            &self.surfaces[..size]
        })
    }

    /// Decode the top surface to tightly packed RGBA8.
    pub fn decode_rgba(&self) -> Result<Vec<u8>> {
        let src = self.top_surface()?;
        let (w, h) = (self.width as usize, self.height as usize);
        match self.format {
            PixelFormat::Bgra { bits } => {
                let bpp = bits as usize / 8;
                let mut out = Vec::with_capacity(w * h * 4);
                for px in src.chunks_exact(bpp) {
                    out.extend_from_slice(&[
                        px[2],
                        px[1],
                        px[0],
                        if bpp == 4 { px[3] } else { 255 },
                    ]);
                }
                Ok(out)
            }
            PixelFormat::Dxt1 | PixelFormat::Dxt3 | PixelFormat::Dxt5 => {
                let (bw, bh) = (blocks(self.width), blocks(self.height));
                let block_len = if self.format == PixelFormat::Dxt1 {
                    8
                } else {
                    16
                };
                let pitch = bw * 4 * 4;
                let mut padded = vec![0u8; pitch * bh * 4];
                for by in 0..bh {
                    for bx in 0..bw {
                        let block = &src[(by * bw + bx) * block_len..][..block_len];
                        let dst = &mut padded[by * 4 * pitch + bx * 16..];
                        match self.format {
                            PixelFormat::Dxt1 => bcdec_rs::bc1(block, dst, pitch),
                            PixelFormat::Dxt3 => bcdec_rs::bc2(block, dst, pitch),
                            PixelFormat::Dxt5 => bcdec_rs::bc3(block, dst, pitch),
                            PixelFormat::Bgra { .. } => unreachable!(),
                        }
                    }
                }
                if bw * 4 == w && bh * 4 == h {
                    return Ok(padded);
                }
                let mut out = Vec::with_capacity(w * h * 4);
                for row in 0..h {
                    out.extend_from_slice(&padded[row * pitch..row * pitch + w * 4]);
                }
                Ok(out)
            }
        }
    }

    /// Encode the top surface as a PNG.
    pub fn to_png(&self) -> Result<Vec<u8>> {
        let rgba = self.decode_rgba()?;
        let mut buf = IoCursor::new(Vec::new());
        {
            let mut enc = png::Encoder::new(&mut buf, self.width, self.height);
            enc.set_color(png::ColorType::Rgba);
            enc.set_depth(png::BitDepth::Eight);
            let mut writer = enc.write_header().context("writing PNG header")?;
            writer.write_image_data(&rgba).context("writing PNG data")?;
        }
        Ok(buf.into_inner())
    }
}

/// Human-readable summary for `tqextract tex info`.
pub fn describe(tex: &TexFile<'_>) -> String {
    let mut out = String::new();
    let _ = writeln!(out, "tex version         {}", tex.version);
    let _ = writeln!(out, "  unknown word      {}", tex.unknown);
    if let Some(flag) = tex.flag {
        let _ = writeln!(out, "  v2 flag           {flag}");
    }
    let _ = writeln!(out, "  dds length        {}", tex.dds_len);
    let _ = writeln!(out, "  trailing bytes    {}", tex.trailing);
    let _ = writeln!(out, "dds");
    let _ = writeln!(
        out,
        "  magic             {}",
        if tex.reversed_mips {
            "DDSR (reversed mips)"
        } else {
            "DDS "
        }
    );
    let _ = writeln!(out, "  size              {}x{}", tex.width, tex.height);
    let _ = writeln!(out, "  mips              {}", tex.mip_count);
    let _ = writeln!(out, "  format            {:?}", tex.format);
    let _ = writeln!(
        out,
        "  fourcc            {:?}",
        String::from_utf8_lossy(&tex.fourcc)
    );
    let _ = writeln!(out, "  masks             {:#010x?}", tex.masks);
    let _ = writeln!(
        out,
        "  surfaces          {} bytes present, {} expected for the mip chain",
        tex.surfaces_len(),
        tex.expected_chain_size()
    );
    out
}

/// Convert one `.tex` file to a PNG at `output`, creating parent directories.
pub fn convert_file(input: &Path, output: &Path) -> Result<u64> {
    let bytes = fs::read(input).with_context(|| format!("reading {}", input.display()))?;
    let tex = TexFile::parse(&bytes).with_context(|| format!("parsing {}", input.display()))?;
    let png = tex
        .to_png()
        .with_context(|| format!("converting {}", input.display()))?;
    if let Some(parent) = output.parent() {
        fs::create_dir_all(parent).with_context(|| format!("creating {}", parent.display()))?;
    }
    fs::write(output, &png).with_context(|| format!("writing {}", output.display()))?;
    Ok(png.len() as u64)
}

/// Convert every `.tex` under `input` to a `.png` at the same relative path
/// under `output`. `input` and `output` may be the same directory.
pub fn convert_dir(input: &Path, output: &Path) -> Result<Report> {
    let mut files = Vec::new();
    collect_tex_files(input, &mut files)?;
    let mut report = Report::default();
    for path in &files {
        let relative = path.strip_prefix(input).expect("collected under input");
        let target = output.join(relative).with_extension("png");
        match convert_file(path, &target) {
            Ok(bytes) => {
                report.written += 1;
                report.bytes += bytes;
            }
            Err(err) => report.fail(err),
        }
    }
    Ok(report)
}

/// Every `.tex` file under `dir`, recursively, in directory order.
pub fn collect_tex_files(dir: &Path, out: &mut Vec<PathBuf>) -> Result<()> {
    for entry in fs::read_dir(dir).with_context(|| format!("reading {}", dir.display()))? {
        let path = entry?.path();
        if path.is_dir() {
            collect_tex_files(&path, out)?;
        } else if path
            .extension()
            .is_some_and(|e| e.eq_ignore_ascii_case("tex"))
        {
            out.push(path);
        }
    }
    Ok(())
}

#[cfg(test)]
pub(crate) mod test_support {
    //! Minimal TEX writer for round-trip tests.

    pub struct Dds<'a> {
        pub reversed: bool,
        pub width: u32,
        pub height: u32,
        pub mips: u32,
        /// `Some(fourcc)` for compressed, `None` for uncompressed at `bits`.
        pub fourcc: Option<&'a [u8; 4]>,
        pub bits: u32,
        pub surfaces: &'a [u8],
    }

    pub fn build(version: u8, dds: &Dds<'_>) -> Vec<u8> {
        let mut d = Vec::new();
        d.extend_from_slice(if dds.reversed { b"DDSR" } else { b"DDS " });
        for v in [124u32, 0x1007, dds.height, dds.width, 0, 0, dds.mips] {
            d.extend_from_slice(&v.to_le_bytes());
        }
        d.extend_from_slice(&[0u8; 44]);
        d.extend_from_slice(&32u32.to_le_bytes());
        match dds.fourcc {
            Some(cc) => {
                d.extend_from_slice(&4u32.to_le_bytes());
                d.extend_from_slice(cc);
                d.extend_from_slice(&0u32.to_le_bytes());
            }
            None => {
                d.extend_from_slice(&0x40u32.to_le_bytes());
                d.extend_from_slice(&[0; 4]);
                d.extend_from_slice(&dds.bits.to_le_bytes());
            }
        }
        d.extend_from_slice(&[0u8; 16]); // masks
        d.extend_from_slice(&[0u8; 20]); // caps + reserved
        assert_eq!(d.len(), 128);
        d.extend_from_slice(dds.surfaces);

        let mut f = Vec::new();
        f.extend_from_slice(b"TEX");
        f.push(version);
        f.extend_from_slice(&0u32.to_le_bytes());
        if version == 2 {
            f.push(1);
        }
        f.extend_from_slice(&(d.len() as u32).to_le_bytes());
        f.extend_from_slice(&d);
        f
    }
}

#[cfg(test)]
mod tests {
    use super::test_support::{Dds, build};
    use super::*;

    /// A DXT1 block that decodes to a solid colour: both endpoints equal,
    /// all indices 0. 0xF800 is pure red in RGB565.
    fn red_block() -> [u8; 8] {
        [0x00, 0xF8, 0x00, 0xF8, 0, 0, 0, 0]
    }
    fn blue_block() -> [u8; 8] {
        [0x1F, 0x00, 0x1F, 0x00, 0, 0, 0, 0]
    }

    #[test]
    fn decodes_v1_uncompressed_bgra() {
        // 2x1, BGRA bytes: pixel 0 = red opaque, pixel 1 = green half alpha.
        let surface = [0, 0, 255, 255, 0, 255, 0, 128];
        let file = build(
            1,
            &Dds {
                reversed: true,
                width: 2,
                height: 1,
                mips: 1,
                fourcc: None,
                bits: 32,
                surfaces: &surface,
            },
        );
        let tex = TexFile::parse(&file).unwrap();
        assert_eq!(tex.version, 1);
        assert_eq!(tex.flag, None);
        assert_eq!(tex.format, PixelFormat::Bgra { bits: 32 });
        assert_eq!(
            tex.decode_rgba().unwrap(),
            vec![255, 0, 0, 255, 0, 255, 0, 128]
        );
    }

    #[test]
    fn decodes_24_bit_with_opaque_alpha() {
        let surface = [0, 0, 255];
        let file = build(
            1,
            &Dds {
                reversed: false,
                width: 1,
                height: 1,
                mips: 1,
                fourcc: None,
                bits: 24,
                surfaces: &surface,
            },
        );
        let tex = TexFile::parse(&file).unwrap();
        assert_eq!(tex.decode_rgba().unwrap(), vec![255, 0, 0, 255]);
    }

    #[test]
    fn reversed_mips_take_the_last_surface() {
        // 4x4 DXT1 with 3 mips (4x4, 2x2, 1x1): one block each. Stored
        // smallest first: [blue 1x1][blue 2x2][red 4x4].
        let mut surfaces = Vec::new();
        surfaces.extend_from_slice(&blue_block());
        surfaces.extend_from_slice(&blue_block());
        surfaces.extend_from_slice(&red_block());
        let file = build(
            2,
            &Dds {
                reversed: true,
                width: 4,
                height: 4,
                mips: 3,
                fourcc: Some(b"DXT1"),
                bits: 0,
                surfaces: &surfaces,
            },
        );
        let tex = TexFile::parse(&file).unwrap();
        assert_eq!(tex.version, 2);
        assert_eq!(tex.flag, Some(1));
        assert_eq!(tex.expected_chain_size(), 24);
        assert_eq!(tex.surfaces_len(), 24);
        let rgba = tex.decode_rgba().unwrap();
        assert_eq!(rgba.len(), 4 * 4 * 4);
        assert!(
            rgba.chunks(4).all(|p| p == [255, 0, 0, 255]),
            "expected solid red, got {:?}",
            &rgba[..8]
        );
    }

    #[test]
    fn forward_mips_take_the_first_surface() {
        let mut surfaces = Vec::new();
        surfaces.extend_from_slice(&red_block());
        surfaces.extend_from_slice(&blue_block());
        surfaces.extend_from_slice(&blue_block());
        let file = build(
            1,
            &Dds {
                reversed: false,
                width: 4,
                height: 4,
                mips: 3,
                fourcc: Some(b"DXT1"),
                bits: 0,
                surfaces: &surfaces,
            },
        );
        let tex = TexFile::parse(&file).unwrap();
        let rgba = tex.decode_rgba().unwrap();
        assert!(rgba.chunks(4).all(|p| p == [255, 0, 0, 255]));
    }

    #[test]
    fn crops_non_multiple_of_four_dimensions() {
        // 6x3 DXT1: 2x1 blocks, 16 bytes, all red.
        let mut surfaces = Vec::new();
        surfaces.extend_from_slice(&red_block());
        surfaces.extend_from_slice(&red_block());
        let file = build(
            1,
            &Dds {
                reversed: false,
                width: 6,
                height: 3,
                mips: 1,
                fourcc: Some(b"DXT1"),
                bits: 0,
                surfaces: &surfaces,
            },
        );
        let tex = TexFile::parse(&file).unwrap();
        let rgba = tex.decode_rgba().unwrap();
        assert_eq!(rgba.len(), 6 * 3 * 4);
        assert!(rgba.chunks(4).all(|p| p == [255, 0, 0, 255]));
    }

    #[test]
    fn png_round_trip_decodes_to_same_pixels() {
        let surface = [0, 0, 255, 255, 0, 255, 0, 128];
        let file = build(
            1,
            &Dds {
                reversed: true,
                width: 2,
                height: 1,
                mips: 1,
                fourcc: None,
                bits: 32,
                surfaces: &surface,
            },
        );
        let tex = TexFile::parse(&file).unwrap();
        let png_bytes = tex.to_png().unwrap();
        let decoder = png::Decoder::new(IoCursor::new(png_bytes));
        let mut reader = decoder.read_info().unwrap();
        let mut buf = vec![0; reader.output_buffer_size().unwrap()];
        let info = reader.next_frame(&mut buf).unwrap();
        assert_eq!((info.width, info.height), (2, 1));
        assert_eq!(&buf[..8], &[255, 0, 0, 255, 0, 255, 0, 128]);
    }

    #[test]
    fn rejects_bad_magic_and_version() {
        assert!(TexFile::parse(b"NOPE").is_err());
        let mut file = build(
            1,
            &Dds {
                reversed: false,
                width: 1,
                height: 1,
                mips: 1,
                fourcc: None,
                bits: 32,
                surfaces: &[0; 4],
            },
        );
        file[3] = 9;
        let err = TexFile::parse(&file).unwrap_err();
        assert!(err.to_string().contains("version 9"), "{err}");
    }

    #[test]
    fn rejects_short_surface_data() {
        let file = build(
            1,
            &Dds {
                reversed: false,
                width: 4,
                height: 4,
                mips: 1,
                fourcc: None,
                bits: 32,
                surfaces: &[0; 8],
            },
        );
        let tex = TexFile::parse(&file).unwrap();
        let err = tex.decode_rgba().unwrap_err();
        assert!(err.to_string().contains("top surface needs"), "{err}");
    }

    fn dxt_4x4(fourcc: &'static [u8; 4], block: &[u8]) -> Vec<u8> {
        build(
            1,
            &Dds {
                reversed: false,
                width: 4,
                height: 4,
                mips: 1,
                fourcc: Some(fourcc),
                bits: 0,
                surfaces: block,
            },
        )
    }

    #[test]
    fn dxt3_explicit_alpha_is_decoded() {
        // DXT3: 8 bytes of 4-bit alphas (row-major, low nibble first), then a
        // DXT1 colour block. Alphas 0xF,0x0 alternate; colour solid red.
        let mut block = vec![0x0F, 0x0F, 0x0F, 0x0F, 0x0F, 0x0F, 0x0F, 0x0F];
        block.extend_from_slice(&red_block());
        let file = dxt_4x4(b"DXT3", &block);
        let tex = TexFile::parse(&file).unwrap();
        assert_eq!(tex.format, PixelFormat::Dxt3);
        let rgba = tex.decode_rgba().unwrap();
        let alphas: Vec<u8> = rgba.chunks(4).map(|p| p[3]).collect();
        // Each byte holds two pixels: low nibble 0xF -> 255, high nibble 0x0 -> 0.
        assert_eq!(&alphas[..4], &[255, 0, 255, 0]);
        assert!(rgba.chunks(4).all(|p| p[..3] == [255, 0, 0]));
    }

    #[test]
    fn dxt5_interpolated_alpha_is_decoded() {
        // DXT5: alpha0, alpha1, then 48 bits of 3-bit indices, then a DXT1
        // colour block. Index 0 selects alpha0 (200) everywhere.
        let mut block = vec![200, 10, 0, 0, 0, 0, 0, 0];
        block.extend_from_slice(&red_block());
        let file = dxt_4x4(b"DXT5", &block);
        let tex = TexFile::parse(&file).unwrap();
        assert_eq!(tex.format, PixelFormat::Dxt5);
        let rgba = tex.decode_rgba().unwrap();
        assert!(
            rgba.chunks(4).all(|p| p == [255, 0, 0, 200]),
            "{:?}",
            &rgba[..8]
        );

        // Index 1 everywhere (bits 001 repeated) selects alpha1.
        let mut block = vec![200, 10, 0b0100_1001, 0b1001_0010, 0b0010_0100];
        block.extend_from_slice(&[0b0100_1001, 0b1001_0010, 0b0010_0100]);
        block.extend_from_slice(&red_block());
        let file = dxt_4x4(b"DXT5", &block);
        let tex = TexFile::parse(&file).unwrap();
        let rgba = tex.decode_rgba().unwrap();
        assert!(
            rgba.chunks(4).all(|p| p == [255, 0, 0, 10]),
            "{:?}",
            &rgba[..8]
        );
    }
}
