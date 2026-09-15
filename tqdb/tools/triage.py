"""
Classify every leaf difference between a website baseline and a parser output.

usage, from the repo root:

  docker compose run --rm -T dev uv run --frozen python tqdb/tools/triage.py \
      output/baseline/tqdb.en.1.4.3.json output/tqdb.en.1.4.3.json en output/diff

Reuses the keying and walk from diffjson.py (same directory). Writes
OUT_DIR/triage-<locale>.md and OUT_DIR/triage-<locale>.json.
"""
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.argv, argv = sys.argv[:1], sys.argv[1:]
baseline_file, new_file, locale, out_dir = argv
out_dir = Path(out_dir)

# diffjson runs at import; feed it its own arguments through a throwaway dir.
sys.argv = ["diffjson.py", baseline_file, new_file, str(out_dir / f"raw-{locale}")]
sys.path.insert(0, str(Path(__file__).parent))
import diffjson  # noqa: E402

bc, nc = diffjson.bc, diffjson.nc

# Differences the English triage already explains.
KNOWN_KEYS = {
    "creatures": {"tagMonsterName382", "~ Toxeanubis the Slayer  ~"},
    "skills": {"unnamed-251", "unnamed-252"},
}


def pieces(s):
    return sorted(p.strip() for p in s.split(","))


def classify(coll, key, path, old, new):
    if key in KNOWN_KEYS.get(coll, ()):
        return "known: Typhon / skill suffix swap"
    if isinstance(old, str) and isinstance(new, str):
        if pieces(old) == pieces(new):
            return "declension reorder"
        if old.strip() == new.strip():
            return "whitespace"
        return "text change"
    if old is None or new is None:
        return "field added/removed"
    return "value change"


rows = defaultdict(list)
counts = Counter()
per_coll = defaultdict(Counter)
added = {}
removed = {}

for coll in sorted(set(bc) | set(nc)):
    b = bc.get(coll, {})
    n = nc.get(coll, {})
    a = sorted(set(n) - set(b))
    r = sorted(set(b) - set(n))
    if a:
        added[coll] = a
    if r:
        removed[coll] = r
    for k in sorted(set(b) & set(n)):
        changes = []
        diffjson.walk(b[k], n[k], "", changes)
        for p, old, new in changes:
            cat = classify(coll, k, p, old, new)
            counts[cat] += 1
            per_coll[coll][cat] += 1
            rows[cat].append({"collection": coll, "key": k, "path": p, "old": old, "new": new})

out = []
out.append(f"# triage {locale}: {Path(baseline_file).name} -> {Path(new_file).name}\n\n")
out.append("| category | leaf changes |\n|---|---|\n")
for cat, c in counts.most_common():
    out.append(f"| {cat} | {c} |\n")
out.append("\n## added / removed entries\n\n")
for coll, ks in added.items():
    out.append(f"- added in {coll} ({len(ks)}): " + ", ".join(ks[:10]) + ("…" if len(ks) > 10 else "") + "\n")
for coll, ks in removed.items():
    out.append(f"- removed from {coll} ({len(ks)}): " + ", ".join(ks[:10]) + ("…" if len(ks) > 10 else "") + "\n")
out.append("\n## per collection\n\n")
for coll, cs in per_coll.items():
    out.append(f"- {coll}: " + ", ".join(f"{cat} {c}" for cat, c in cs.most_common()) + "\n")
for cat in ("text change", "whitespace", "value change", "field added/removed", "declension reorder"):
    if not rows[cat]:
        continue
    out.append(f"\n## {cat} ({len(rows[cat])})\n\n")
    # Group by (old, new) so a repeated wording change is one line.
    grouped = Counter()
    example = {}
    for row in rows[cat]:
        sig = (json.dumps(row["old"], ensure_ascii=False), json.dumps(row["new"], ensure_ascii=False))
        grouped[sig] += 1
        example.setdefault(sig, row)
    out.append(f"{len(grouped)} distinct old/new pairs.\n\n| n | where | old | new |\n|---|---|---|---|\n")
    for sig, c in grouped.most_common(60):
        ex = example[sig]
        where = f"{ex['collection']} {ex['key']} `{diffjson.norm(ex['path'])}`"
        out.append(f"| {c} | {where} | {diffjson.short(ex['old'], 70)} | {diffjson.short(ex['new'], 70)} |\n")

(out_dir / f"triage-{locale}.md").write_text("".join(out), encoding="utf8")
json.dump(
    {"counts": counts, "added": added, "removed": removed, "rows": rows},
    open(out_dir / f"triage-{locale}.json", "w", encoding="utf8"),
    ensure_ascii=False,
    indent=1,
)
print(locale, dict(counts), "added", {k: len(v) for k, v in added.items()}, "removed", {k: len(v) for k, v in removed.items()})
