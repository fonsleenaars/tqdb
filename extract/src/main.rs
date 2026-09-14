//! `tqextract`: in-house replacement for ARZExtractor.exe, the game's
//! ArchiveTool.exe, and TextureViewer.exe. Format notes: `docs/game-formats.md`.

use std::fs;
use std::path::{Path, PathBuf};
use std::time::Instant;

use anyhow::{Context, Result, bail};
use clap::{Parser, Subcommand};

use tqextract::{Report, arc, arz, prepare, tex};

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
    /// Read an ARC archive (Templates.arc, Text_XX.arc, Items.arc, ...).
    Arc {
        #[command(subcommand)]
        command: ArcCommand,
    },
    /// Read TEX textures.
    Tex {
        #[command(subcommand)]
        command: TexCommand,
    },
    /// Run every extraction a parser run needs, from a game install to a data directory.
    Prepare {
        /// Root of the Titan Quest Anniversary Edition install
        game: PathBuf,
        /// Data directory to populate (see docs/setup.md for the layout)
        data: PathBuf,
        /// Print the plan and exit without extracting anything
        #[arg(long)]
        dry_run: bool,
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

#[derive(Subcommand)]
enum ArcCommand {
    /// Print header fields, counts, and a sample of entries without extracting.
    Info {
        /// Path to an .arc file
        input: PathBuf,
    },
    /// Extract every entry into a directory (lowercased paths).
    Extract {
        /// Path to an .arc file
        input: PathBuf,
        /// Directory that will receive the archive contents
        output: PathBuf,
    },
}

#[derive(Subcommand)]
enum TexCommand {
    /// Print the TEX and DDS header fields of one texture.
    Info {
        /// Path to a .tex file
        input: PathBuf,
    },
    /// Convert one texture to PNG.
    Convert {
        /// Path to a .tex file
        input: PathBuf,
        /// Path of the PNG to write
        output: PathBuf,
    },
    /// Convert every .tex under a directory to a .png at the same relative path.
    ConvertDir {
        /// Directory to walk
        input: PathBuf,
        /// Directory to write into (may equal input)
        output: PathBuf,
    },
    /// Parse and decode every .tex under a directory and print a histogram of what was found.
    Survey {
        /// Directory to walk
        dir: PathBuf,
    },
}

fn main() -> Result<()> {
    let cli = Cli::parse();
    match cli.command {
        Command::Arz { command } => match command {
            ArzCommand::Info { input } => arz_info(&input),
            ArzCommand::Extract { input, output } => arz_extract(&input, &output),
        },
        Command::Arc { command } => match command {
            ArcCommand::Info { input } => arc_info(&input),
            ArcCommand::Extract { input, output } => arc_extract(&input, &output),
        },
        Command::Tex { command } => match command {
            TexCommand::Info { input } => tex_info(&input),
            TexCommand::Convert { input, output } => tex_convert(&input, &output),
            TexCommand::ConvertDir { input, output } => tex_convert_dir(&input, &output),
            TexCommand::Survey { dir } => tex_survey(&dir),
        },
        Command::Prepare {
            game,
            data,
            dry_run,
        } => run_prepare(&game, &data, dry_run),
    }
}

/// Print a report and turn any failures into a non-zero exit.
fn finish(what: &str, report: &Report, elapsed: std::time::Duration) -> Result<()> {
    for err in &report.errors {
        eprintln!("error: {err}");
    }
    eprintln!(
        "{what}: {} written ({} bytes) in {elapsed:.1?}{}",
        report.written,
        report.bytes,
        if report.is_ok() {
            String::new()
        } else {
            format!(", {} failed", report.errors.len())
        }
    );
    if !report.is_ok() {
        bail!("{} failures", report.errors.len());
    }
    Ok(())
}

// --- arz -------------------------------------------------------------------

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
    eprintln!("{} records in {}", arz.records().len(), input.display());
    let report = arz.extract_all(output, |done, total| eprintln!("  {done}/{total}"));
    finish("arz extract", &report, started.elapsed())
}

// --- arc -------------------------------------------------------------------

fn load_arc(input: &Path) -> Result<arc::ArcFile> {
    let bytes = fs::read(input).with_context(|| format!("reading {}", input.display()))?;
    arc::ArcFile::parse(bytes).with_context(|| format!("parsing {}", input.display()))
}

fn arc_info(input: &Path) -> Result<()> {
    let arc = load_arc(input)?;
    print!("{}", arc::describe(&arc));

    // Decode every entry as a probe: sizes and checksums must all agree.
    let mut failures = 0;
    for entry in arc.entries() {
        if let Err(err) = arc.read_entry(entry) {
            failures += 1;
            eprintln!("error: {err:#}");
        }
    }
    println!(
        "decoded {} of {} entries with matching length and adler32",
        arc.entries().len() - failures,
        arc.entries().len()
    );
    if failures > 0 {
        bail!("{failures} entries failed to decode");
    }
    Ok(())
}

fn arc_extract(input: &Path, output: &Path) -> Result<()> {
    let started = Instant::now();
    let arc = load_arc(input)?;
    let report = arc.extract_all(output);
    finish("arc extract", &report, started.elapsed())
}

// --- tex -------------------------------------------------------------------

fn tex_info(input: &Path) -> Result<()> {
    let bytes = fs::read(input).with_context(|| format!("reading {}", input.display()))?;
    let tex =
        tex::TexFile::parse(&bytes).with_context(|| format!("parsing {}", input.display()))?;
    print!("{}", tex::describe(&tex));
    let rgba = tex.decode_rgba()?;
    println!("decoded             {} RGBA bytes", rgba.len());
    Ok(())
}

fn tex_convert(input: &Path, output: &Path) -> Result<()> {
    tex::convert_file(input, output)?;
    Ok(())
}

fn tex_convert_dir(input: &Path, output: &Path) -> Result<()> {
    let started = Instant::now();
    let report = tex::convert_dir(input, output)?;
    finish("tex convert-dir", &report, started.elapsed())
}

fn tex_survey(dir: &Path) -> Result<()> {
    use std::collections::BTreeMap;

    let started = Instant::now();
    let mut files = Vec::new();
    tex::collect_tex_files(dir, &mut files)?;

    let mut by_key: BTreeMap<String, usize> = BTreeMap::new();
    let mut chain_mismatch = 0usize;
    let mut failures: Vec<(PathBuf, String)> = Vec::new();

    for path in &files {
        let bytes = match fs::read(path) {
            Ok(b) => b,
            Err(e) => {
                failures.push((path.clone(), e.to_string()));
                continue;
            }
        };
        let tex = match tex::TexFile::parse(&bytes) {
            Ok(t) => t,
            Err(e) => {
                failures.push((path.clone(), format!("{e:#}")));
                continue;
            }
        };
        let key = format!(
            "v{} {} {:?} mips={} trailing={}",
            tex.version,
            if tex.reversed_mips { "DDSR" } else { "DDS " },
            tex.format,
            if tex.mip_count > 1 { ">1" } else { "1" },
            if tex.trailing > 0 { ">0" } else { "0" },
        );
        *by_key.entry(key).or_default() += 1;
        if tex.surfaces_len() != tex.expected_chain_size() {
            chain_mismatch += 1;
        }
        if let Err(e) = tex.decode_rgba() {
            failures.push((path.clone(), format!("{e:#}")));
        }
    }

    println!(
        "{} .tex files under {} in {:.1?}",
        files.len(),
        dir.display(),
        started.elapsed()
    );
    for (key, n) in &by_key {
        println!("  {n:>7}  {key}");
    }
    println!("mip chain size differs from header expectation: {chain_mismatch}");
    println!("failures: {}", failures.len());
    for (path, err) in failures.iter().take(20) {
        println!("  {}: {err}", path.display());
    }
    if !failures.is_empty() {
        bail!("{} of {} textures failed", failures.len(), files.len());
    }
    Ok(())
}

// --- prepare ---------------------------------------------------------------

fn run_prepare(game: &Path, data: &Path, dry_run: bool) -> Result<()> {
    let started = Instant::now();
    let steps = prepare::plan(game, data)?;

    eprintln!(
        "{} steps from {} into {}",
        steps.len(),
        game.display(),
        data.display()
    );
    for step in &steps {
        eprintln!(
            "  {:<9} {}  ->  {}",
            format!("{:?}", step.kind).to_lowercase(),
            step.source
                .strip_prefix(game)
                .unwrap_or(&step.source)
                .display(),
            step.target
                .strip_prefix(data)
                .unwrap_or(&step.target)
                .display()
        );
    }
    if dry_run {
        return Ok(());
    }

    let mut total = Report::default();
    for step in &steps {
        let name = step
            .source
            .strip_prefix(game)
            .unwrap_or(&step.source)
            .display()
            .to_string();
        let (report, elapsed) = prepare::run(step).with_context(|| format!("step {name}"))?;
        eprintln!(
            "{name}: {} written ({} bytes) in {elapsed:.1?}{}",
            report.written,
            report.bytes,
            if report.is_ok() {
                String::new()
            } else {
                format!(", {} failed", report.errors.len())
            }
        );
        for err in &report.errors {
            eprintln!("  error: {err}");
        }
        total.written += report.written;
        total.bytes += report.bytes;
        total.errors.extend(report.errors);
    }
    finish("prepare", &total, started.elapsed())
}
