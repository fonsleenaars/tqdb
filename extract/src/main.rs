//! `tqextract`: in-house replacement for ARZExtractor.exe, the game's
//! ArchiveTool.exe, and TextureViewer.exe. Format notes: `docs/game-formats.md`.

use std::collections::HashSet;
use std::fs;
use std::path::{Path, PathBuf};
use std::time::Instant;

use anyhow::{Context, Result, bail};
use clap::{Parser, Subcommand};

use tqextract::arz;

#[derive(Parser)]
#[command(version, about, long_about = None)]
struct Cli {
    #[command(subcommand)]
    command: Command,
}

#[derive(Subcommand)]
enum Command {
    /// Read an ARZ database (database.arz).
    Arz {
        #[command(subcommand)]
        command: ArzCommand,
    },
    /// Extract every file from an ARC archive.
    Arc {
        /// Path to an .arc file
        input: PathBuf,
        /// Directory that will receive the archive contents
        output: PathBuf,
    },
    /// Convert a TEX texture to PNG.
    Tex {
        /// Path to a .tex file
        input: PathBuf,
        /// Path of the PNG to write
        output: PathBuf,
    },
    /// Run every extraction a parser run needs, from a game install to a data directory.
    Prepare {
        /// Root of the Titan Quest Anniversary Edition install
        game: PathBuf,
        /// Data directory to populate (see docs/setup.md for the layout)
        data: PathBuf,
    },
}

#[derive(Subcommand)]
enum ArzCommand {
    /// Print header fields, counts, and a sample of records without extracting.
    Info {
        /// Path to database.arz
        input: PathBuf,
    },
    /// Extract every record into a tree of DBR text files.
    Extract {
        /// Path to database.arz
        input: PathBuf,
        /// Directory that will receive records/**/*.dbr (lowercased paths)
        output: PathBuf,
    },
}

fn main() -> Result<()> {
    let cli = Cli::parse();
    match cli.command {
        Command::Arz { command } => match command {
            ArzCommand::Info { input } => arz_info(&input),
            ArzCommand::Extract { input, output } => arz_extract(&input, &output),
        },
        Command::Arc { input, output } => bail!(
            "arc extraction is not implemented yet ({} -> {})",
            input.display(),
            output.display()
        ),
        Command::Tex { input, output } => bail!(
            "tex conversion is not implemented yet ({} -> {})",
            input.display(),
            output.display()
        ),
        Command::Prepare { game, data } => bail!(
            "prepare is not implemented yet ({} -> {})",
            game.display(),
            data.display()
        ),
    }
}

fn load_arz(input: &Path) -> Result<arz::ArzFile> {
    let bytes = fs::read(input).with_context(|| format!("reading {}", input.display()))?;
    arz::ArzFile::parse(bytes).with_context(|| format!("parsing {}", input.display()))
}

fn arz_info(input: &Path) -> Result<()> {
    let arz = load_arz(input)?;
    print!("{}", arz::describe(&arz));

    // Decode the first record fully, as a probe of the payload format.
    if let Some(first) = arz.records().first() {
        let record = arz.read_record(first)?;
        println!(
            "first record decoded ({} variables)",
            record.variables.len()
        );
        for line in record.to_dbr().lines().take(8) {
            println!("  {line}");
        }
    }
    Ok(())
}

fn arz_extract(input: &Path, output: &Path) -> Result<()> {
    let started = Instant::now();
    let arz = load_arz(input)?;
    let total = arz.records().len();
    eprintln!("{total} records in {}", input.display());

    let mut created_dirs: HashSet<PathBuf> = HashSet::new();
    let mut failures = 0usize;

    for (i, info) in arz.records().iter().enumerate() {
        let path = output.join(arz::dbr_path(&info.name));
        let result = arz.read_record(info).and_then(|record| {
            if let Some(parent) = path.parent()
                && created_dirs.insert(parent.to_path_buf())
            {
                fs::create_dir_all(parent)
                    .with_context(|| format!("creating {}", parent.display()))?;
            }
            fs::write(&path, record.to_dbr()).with_context(|| format!("writing {}", path.display()))
        });
        if let Err(err) = result {
            failures += 1;
            eprintln!("error: {err:#}");
        }
        if (i + 1) % 10_000 == 0 {
            eprintln!("  {}/{total}", i + 1);
        }
    }

    eprintln!(
        "wrote {} records to {} in {:.1?}",
        total - failures,
        output.display(),
        started.elapsed()
    );
    if failures > 0 {
        bail!("{failures} of {total} records failed");
    }
    Ok(())
}
