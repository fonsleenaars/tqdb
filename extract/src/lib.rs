//! Readers for the Titan Quest container formats. Format notes and the source
//! implementations they were derived from are in `docs/game-formats.md`.

pub mod arc;
pub mod arz;
mod cursor;
pub mod prepare;
pub mod tex;

/// Outcome of a bulk extraction or conversion. Per-item failures are
/// collected rather than aborting, so one bad file does not hide the rest.
#[derive(Debug, Default)]
pub struct Report {
    pub written: usize,
    pub bytes: u64,
    pub errors: Vec<String>,
}

impl Report {
    pub fn is_ok(&self) -> bool {
        self.errors.is_empty()
    }

    pub fn fail(&mut self, err: anyhow::Error) {
        self.errors.push(format!("{err:#}"));
    }
}
