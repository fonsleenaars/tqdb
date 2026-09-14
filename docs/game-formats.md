# Game file formats

What the parser reads, at two levels: the extracted text formats it consumes today, and the binary containers those are extracted from. The binary sections come from reading open-source implementations; each says whether it has also been verified against the real game files.

## Extracted formats (what the Python parser reads)

### DBR records

One text file per game record, path like `records/item/equipmentweapon/sword/x2_sword_01.dbr`. Comma-separated, one property per line, trailing comma, arrays joined with `;`:

```
templateName,database\templates\weaponmelee_sword.tpl,
Class,WeaponMelee_Sword,
offensivePhysicalMin,12;14;16,
itemLevel,20,
```

Only the first comma splits key from value. Keys are typed by the record's template; undeclared keys are ignored. `templateName` and `Class` both identify the template. Game paths inside values use backslashes and mixed case; the parser lowercases them.

### TPL templates

`.tpl` files under `data/database/templates/`, one per record class, brace-delimited:

```
Group
{
    name = "Header"
    Variable
    {
        name = "templateName"
        class = "static"
        type = "include"
        defaultValue = "%TEMPLATE_DIR%database\templates\templatebase\itembase.tpl"
    }
}
```

Variable `class` is `static`, `variable`, `array`, or `picklist`. Variable `type` is `include`, `file_dbr`, `file_tex`, `string`, `real`, `int`, or `bool`. A `static include` variable is a template reference; its referenced template's non-static variables are inherited. The `Class` variable's `defaultValue` names the record class.

### Text resources

`data/resources/<locale>/*.txt`, one directory per locale (`cs de en es fr it ja ko pl ru uk zh`; the game's Chinese archive is `Text_CH.arc`). UTF-16 with BOM. Lines are `key=value`, `//` comments. Two families:

- **Tags** (names): `commonequipment.txt`, `x2skills.txt`, `x4mainquest_nonvoiced.txt` and 31 more. Keys like `tagWeapon_Sword_01`.
- **UI strings** (property templates): `ui.txt`, `xui.txt`, `x2ui.txt`, `x3basegame_nonvoiced.txt`, `x4basegame_nonvoiced.txt`. Values carry the game's own placeholder syntax, e.g. `{%.0f0}% Chance of `, and declension markers like `[ms]`/`[fs]`.

Tag prefixes are semantic: `x2`, `x3`, `x4` mark Ragnarök, Atlantis, and Eternal Embers content respectively. The website derives DLC badges from them.

### Quest files

`data/quests/*.qst` are binary. The parser does not decode them; it lowercases the printable bytes and regex-scrapes `titletag<tag>` and reward record paths. Format unknown beyond that.

### Textures

`.tex` files, see below. Only item icons are converted (single frame, one mipmap in practice).

## Binary containers (what an in-house extractor must read)

All integers little-endian.

### ARZ (`Database/database.arz`)

Verified against TQVaultAE (C#, MIT) and tqdatabase (Java, GPL) source, and on 2026-09-14 against the real Anniversary Edition file with `tqextract arz`: every table size matched the header exactly, all 74,013 records inflated and decoded, and the 190,522-entry string table read cleanly.

```
Header, 24 bytes
  0x00 i32  unknown; 0x0003_0004 in TQ AE (Grim Dawn writes 0x0003_0002); readers ignore it
  0x04 i32  recordTableStart
  0x08 i32  recordTableSize
  0x0C i32  recordCount
  0x10 i32  stringTableStart
  0x14 i32  stringTableSize
Record data follows the header; record offsets are relative to file offset 24.

String table at stringTableStart
  i32 count, then count × { i32 len, len bytes cp1252 }      length-prefixed, not null-terminated

Record table at recordTableStart, per record
  i32 nameStringIndex           → the .dbr path
  i32 typeLen, typeLen bytes    → record class string
  i32 offset (+24)
  i32 compressedSize
  i32, i32                      ignored by TQ readers (Grim Dawn: decompressedSize + filetime)

Record payload: one zlib stream. Decompressed length is a multiple of 4.
  repeat until end:
    i16 type    0 = i32, 1 = f32, 2 = string (i32 index into string table), 3 = bool (i32)
    i16 count   ≥ 1; arrays
    i32 nameStringIndex
    count × i32 value
```

About 8,000 records have an empty type string (proxy pools and similar); the type is informational and nothing depends on it.

DBR output is one text file per record at `<out>/<nameString>` with `key,v1;v2,` lines. `tqextract` writes the path lowercased with forward slashes, floats in shortest round-trip form, bools as `0`/`1`, LF line endings. The original ARZExtractor's exact formatting is unknown; no old extract exists to diff against. The full database is 745 MB on disk and extracts in a few seconds.

Grim Dawn's ARZ is the same layout with LZ4 block compression instead of zlib. Grim Dawn tools port to Titan Quest by swapping the decompressor.

### ARC (`Toolset/Templates.arc`, `Text/Text_EN.arc`, `Resources/Items.arc`, `Resources/Quests.arc`, and the `XPack*/` variants)

Verified against TQVaultAE and tqdatabase source, and on 2026-09-14 against the real `Templates.arc` (566 entries) and `Text_EN.arc` (57 entries, including two-part files) with `tqextract arc`: the tables add up to the file length exactly, and every entry decompresses to its stated length with a matching adler32.

```
Header, 28 bytes
  0x00 "ARC\0"        0x04 u32 version (1 in TQ AE; Grim Dawn uses 3)
  0x08 u32 numEntries 0x0C u32 numParts  0x10 u32 partTableSize (= numParts × 12)
  0x14 u32 stringTableSize                0x18 u32 tocOffset

At tocOffset: numParts × { u32 fileOffset, u32 compressedSize, u32 realSize }
Then: file-name string table (names null-terminated)
Then, to the end of the file: numEntries × 44-byte entries
  u32 storageType (1 = stored, 3 = compressed)
  u32 fileOffset, u32 compressedSize, u32 realSize
  u32 adler32 of decompressed data
  u64 filetime
  u32 numParts, u32 firstPartIndex
  u32 nameLen, u32 nameOffset (relative to string table start)
```

A file is the concatenation of its parts; each part is an independent zlib stream. A part with equal compressed and real sizes is a raw copy. Entries with an empty name are deleted. Entry names in the AE archives are already lowercase with forward slashes (`templates/templatebase/itembase.tpl`); `tqextract` normalizes anyway.

### TEX (item icons)

Verified against TQVaultAE, tqdatabase, and the parser's own header patch in `images.py`, and on 2026-09-14 against all 7,070 textures in `Items.arc` and `XPack4/Item.arc` with `tqextract tex survey`: every file parses, every mip chain length matches the header, every surface decodes, and converted icons look right.

```
v1:  "TEX\x01"  u32 (0)  u32 ddsLength           DDS…  offset 12
v2:  "TEX\x02"  u32 (0)  u8 flag  u32 ddsLength  DDS…  offset 13
```

Base-game item textures are all v1; Eternal Embers ones are all v2. The parser downgrades v2 to v1 by removing byte 8.

The embedded DDS has quirks:

- Magic is `DDSR` in every texture seen so far, never `DDS `. **`DDSR` means mipmaps are stored smallest first**; the top-level surface is the *last* `surfaceSize` bytes. Every UI icon has one mip, so single-frame decoders get away with ignoring this; model textures have full chains.
- RGB bit masks are zeroed for uncompressed formats. The bytes are B, G, R, A (A8R8G8B8 little-endian); a 32-bit surface always carries alpha even though `DDPF_ALPHAPIXELS` is not set.
- Pixel formats seen, with counts across both archives: uncompressed 32-bit (3,056), DXT1 (2,216), DXT5 (1,446), DXT3 (338), uncompressed 24-bit (14). **Every UI icon under a `uibitmaps` directory is uncompressed 32-bit.** DXT is used only for mesh, glow, and bump textures.
- No trailing data after the declared DDS length in any file; multi-frame animated TEX files exist elsewhere in the game but not among item textures.

### Reference implementations

| Project | Language | License | Covers | Use |
|---|---|---|---|---|
| [TQVaultAE](https://github.com/EtienneLamoureux/TQVaultAE) | C# | MIT | ARZ, ARC, TEX (via ImageMagick) | primary port source |
| [tqdatabase](https://github.com/epinter/tqdatabase) / tqrespec `tqextract-cli` | Java | GPL-3 | ARZ, ARC, TEX with mipmap reordering | read-only cross-check; working CLI fallback |
| [grimarz](https://github.com/atom0s/grimarz), [grimarc](https://github.com/atom0s/grimarc) | C++ | GPL-3 | Grim Dawn ARZ/ARC (LZ4) | read-only cross-check |
| kraken444444/grim-dawn-save-editor `gdsave/arz.py` | Python | MIT | Grim Dawn ARZ, ~100 lines | reference for a minimal reader |
| `image_dds` + `bcdec_rs`, `ddsfile`, `flate2` | Rust | MIT | DDS decode, DDS header, zlib | building blocks |
| `bcdec.h`, zlib, `stb_image_write` | C | MIT/Unlicense | same, in C | building blocks |

No Rust, Go, or Python crate for TQ or Grim Dawn ARZ/ARC exists on crates.io, PyPI, or GitHub as of September 2026. The three formats total a few hundred lines; porting from the MIT sources is the intended route.

The bundled `utils/arzextractor/ARZExtractor.exe` is a .NET 2.0 C++/CLI repackaging of TQVault's data layer with a WinForms front end, author unknown, 2009. `utils/textureviewer/TextureViewer.exe` is Max McGuire's native Win32 tool over DevIL.
