//! Bounds-checked little-endian reads over a byte slice, shared by the
//! container readers.

use anyhow::{Result, ensure};

pub(crate) struct Cursor<'a> {
    data: &'a [u8],
    pub(crate) pos: usize,
}

impl<'a> Cursor<'a> {
    pub(crate) fn new(data: &'a [u8], pos: usize) -> Self {
        Self { data, pos }
    }

    pub(crate) fn remaining(&self) -> usize {
        self.data.len().saturating_sub(self.pos)
    }

    pub(crate) fn bytes(&mut self, n: usize) -> Result<&'a [u8]> {
        ensure!(
            self.remaining() >= n,
            "unexpected end of data at byte {}: wanted {n} more, {} left",
            self.pos,
            self.remaining()
        );
        let slice = &self.data[self.pos..self.pos + n];
        self.pos += n;
        Ok(slice)
    }

    pub(crate) fn u32(&mut self) -> Result<u32> {
        Ok(u32::from_le_bytes(self.bytes(4)?.try_into().unwrap()))
    }

    pub(crate) fn u64(&mut self) -> Result<u64> {
        Ok(u64::from_le_bytes(self.bytes(8)?.try_into().unwrap()))
    }

    pub(crate) fn i32(&mut self) -> Result<i32> {
        Ok(self.u32()? as i32)
    }

    pub(crate) fn i16(&mut self) -> Result<i16> {
        Ok(i16::from_le_bytes(self.bytes(2)?.try_into().unwrap()))
    }
}

/// The game's strings are Windows-1252, not Latin-1: bytes 0x80..0x9F are
/// printable (euro sign, curly quotes) rather than control characters.
pub(crate) fn decode_cp1252(bytes: &[u8]) -> String {
    let (text, _, _) = encoding_rs::WINDOWS_1252.decode(bytes);
    text.into_owned()
}
