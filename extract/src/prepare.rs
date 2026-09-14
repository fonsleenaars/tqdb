//! `tqextract prepare`: turn a game install into the `data/` tree the parser
//! reads. The layout is documented in `docs/setup.md`:
//!
//! ```text
//! data/
//!   database/records/**/*.dbr        Database/database.arz
//!   database/templates/**/*.tpl      Toolset/Templates.arc
//!   resources/<locale>/*.txt         Text/Text_XX.arc
//!   quests/*.qst                     Resources/Quests.arc + XPack*/Quests.arc, flattened
//!   textures/items/                  Resources/Items.arc, plus a .png beside every .tex
//!   textures/xpack<N>/item(s)/       Resources/XPack<N>/Item(s).arc, likewise
//! ```
//!
//! Every output path is lowercase. File lookups in the game directory are
//! case-insensitive so a copy made on a case-sensitive filesystem works too.

use std::fs;
use std::path::{Path, PathBuf};
use std::time::Instant;

use anyhow::{Context, Result, bail};

use crate::{Report, arc, arz, tex};

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum Kind {
    /// `database.arz` to a DBR tree.
    Arz,
    /// Plain ARC extraction.
    Arc,
    /// ARC extraction followed by TEX to PNG conversion in place.
    Textures,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Step {
    pub kind: Kind,
    pub source: PathBuf,
    pub target: PathBuf,
}

/// Game text archive suffix to the locale code the parser uses.
const LOCALES: &[(&str, &str)] = &[
    ("BR", "br"),
    ("CH", "zh"),
    ("CZ", "cs"),
    ("DE", "de"),
    ("EN", "en"),
    ("ES", "es"),
    ("FR", "fr"),
    ("IT", "it"),
    ("JA", "ja"),
    ("KO", "ko"),
    ("PL", "pl"),
    ("RU", "ru"),
    ("UK", "uk"),
];

/// Work out every extraction for this install. Fails if the database or the
/// templates are missing; expansion archives are optional.
pub fn plan(game: &Path, data: &Path) -> Result<Vec<Step>> {
    let mut steps = Vec::new();

    let database = child(game, "Database").and_then(|d| child(&d, "database.arz"));
    let Some(database) = database else {
        bail!("no Database/database.arz under {}", game.display());
    };
    steps.push(Step {
        kind: Kind::Arz,
        source: database,
        target: data.join("database"),
    });

    let templates = child(game, "Toolset").and_then(|d| child(&d, "Templates.arc"));
    let Some(templates) = templates else {
        bail!("no Toolset/Templates.arc under {}", game.display());
    };
    steps.push(Step {
        kind: Kind::Arc,
        source: templates,
        target: data.join("database"),
    });

    if let Some(text_dir) = child(game, "Text") {
        let mut archives = children_matching(&text_dir, |n| {
            n.to_lowercase().starts_with("text_") && n.to_lowercase().ends_with(".arc")
        })?;
        archives.sort();
        for archive in archives {
            let name = archive.file_stem().and_then(|s| s.to_str()).unwrap_or("");
            let suffix = name.get(5..).unwrap_or("").to_uppercase();
            let locale = LOCALES
                .iter()
                .find(|(s, _)| *s == suffix)
                .map(|(_, l)| (*l).to_string())
                .unwrap_or_else(|| suffix.to_lowercase());
            steps.push(Step {
                kind: Kind::Arc,
                source: archive,
                target: data.join("resources").join(locale),
            });
        }
    }

    let Some(resources) = child(game, "Resources") else {
        bail!("no Resources directory under {}", game.display());
    };
    let mut packs = vec![resources.clone()];
    let mut xpacks = children_matching(&resources, |n| n.to_lowercase().starts_with("xpack"))?;
    xpacks.sort();
    packs.extend(xpacks);

    for pack in &packs {
        let relative = pack.strip_prefix(&resources).unwrap_or(Path::new(""));
        let prefix = relative.to_string_lossy().to_lowercase();

        if let Some(quests) = child(pack, "Quests.arc") {
            steps.push(Step {
                kind: Kind::Arc,
                source: quests,
                target: data.join("quests"),
            });
        }
        for name in ["Items.arc", "Item.arc"] {
            if let Some(items) = child(pack, name) {
                let dir = name.trim_end_matches(".arc").to_lowercase();
                let target = if prefix.is_empty() {
                    data.join("textures").join(dir)
                } else {
                    data.join("textures").join(&prefix).join(dir)
                };
                steps.push(Step {
                    kind: Kind::Textures,
                    source: items,
                    target,
                });
            }
        }
    }

    Ok(steps)
}

/// Execute one step. Returns the report and the elapsed time.
pub fn run(step: &Step) -> Result<(Report, std::time::Duration)> {
    let started = Instant::now();
    let bytes =
        fs::read(&step.source).with_context(|| format!("reading {}", step.source.display()))?;
    let report = match step.kind {
        Kind::Arz => {
            let arz = arz::ArzFile::parse(bytes)
                .with_context(|| format!("parsing {}", step.source.display()))?;
            arz.extract_all(&step.target, |_, _| {})
        }
        Kind::Arc => {
            let arc = arc::ArcFile::parse(bytes)
                .with_context(|| format!("parsing {}", step.source.display()))?;
            arc.extract_all(&step.target)
        }
        Kind::Textures => {
            let arc = arc::ArcFile::parse(bytes)
                .with_context(|| format!("parsing {}", step.source.display()))?;
            let mut report = arc.extract_all(&step.target);
            if report.is_ok() {
                let png = tex::convert_dir(&step.target, &step.target)?;
                report.written += png.written;
                report.bytes += png.bytes;
                report.errors.extend(png.errors);
            }
            report
        }
    };
    Ok((report, started.elapsed()))
}

/// Case-insensitive lookup of a direct child.
fn child(dir: &Path, name: &str) -> Option<PathBuf> {
    let entries = fs::read_dir(dir).ok()?;
    for entry in entries.flatten() {
        if entry
            .file_name()
            .to_string_lossy()
            .eq_ignore_ascii_case(name)
        {
            return Some(entry.path());
        }
    }
    None
}

fn children_matching(dir: &Path, pred: impl Fn(&str) -> bool) -> Result<Vec<PathBuf>> {
    let mut out = Vec::new();
    for entry in fs::read_dir(dir).with_context(|| format!("reading {}", dir.display()))? {
        let entry = entry?;
        if pred(&entry.file_name().to_string_lossy()) {
            out.push(entry.path());
        }
    }
    Ok(out)
}

#[cfg(test)]
mod tests {
    use super::*;

    fn touch(path: &Path) {
        fs::create_dir_all(path.parent().unwrap()).unwrap();
        fs::write(path, b"").unwrap();
    }

    fn fake_install() -> tempfile::TempDir {
        let dir = tempfile::tempdir().unwrap();
        let g = dir.path();
        touch(&g.join("Database/database.arz"));
        touch(&g.join("Toolset/Templates.arc"));
        touch(&g.join("Text/Text_EN.arc"));
        touch(&g.join("Text/Text_CH.arc"));
        touch(&g.join("Text/Text_BR.arc"));
        touch(&g.join("Text/Text_XX.arc"));
        touch(&g.join("Resources/Items.arc"));
        touch(&g.join("Resources/Quests.arc"));
        touch(&g.join("Resources/XPack/Items.arc"));
        touch(&g.join("Resources/XPack/Quests.arc"));
        touch(&g.join("Resources/XPack4/Item.arc"));
        touch(&g.join("Resources/XPack4/Quests.arc"));
        dir
    }

    #[test]
    fn plans_every_archive_with_lowercase_targets() {
        let dir = fake_install();
        let data = Path::new("/data");
        let steps = plan(dir.path(), data).unwrap();
        let targets: Vec<String> = steps
            .iter()
            .map(|s| {
                format!(
                    "{:?} {}",
                    s.kind,
                    s.target.strip_prefix(data).unwrap().display()
                )
            })
            .collect();
        assert_eq!(
            targets,
            vec![
                "Arz database",
                "Arc database",
                "Arc resources/br",
                "Arc resources/zh",
                "Arc resources/en",
                "Arc resources/xx",
                "Arc quests",
                "Textures textures/items",
                "Arc quests",
                "Textures textures/xpack/items",
                "Arc quests",
                "Textures textures/xpack4/item",
            ]
        );
    }

    #[test]
    fn requires_database_and_templates() {
        let dir = tempfile::tempdir().unwrap();
        touch(&dir.path().join("Toolset/Templates.arc"));
        let err = plan(dir.path(), Path::new("/data")).unwrap_err();
        assert!(err.to_string().contains("database.arz"), "{err}");

        touch(&dir.path().join("Database/database.arz"));
        fs::remove_file(dir.path().join("Toolset/Templates.arc")).unwrap();
        let err = plan(dir.path(), Path::new("/data")).unwrap_err();
        assert!(err.to_string().contains("Templates.arc"), "{err}");
    }

    #[test]
    fn lookups_are_case_insensitive() {
        let dir = tempfile::tempdir().unwrap();
        let g = dir.path();
        touch(&g.join("database/DATABASE.ARZ"));
        touch(&g.join("toolset/templates.arc"));
        fs::create_dir_all(g.join("resources")).unwrap();
        let steps = plan(g, Path::new("/data")).unwrap();
        assert_eq!(steps.len(), 2);
        assert!(steps[0].source.ends_with("DATABASE.ARZ"));
    }
}
