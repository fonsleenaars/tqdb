"""
Structural diff of two tqdb output files.

usage, from the repo root:

  docker compose run --rm -T dev uv run --frozen python tqdb/tools/diffjson.py \
      output/baseline/tqdb.en.1.4.3.json output/tqdb.en.1.4.3.json output/diff

Writes OUT_DIR/summary.md (human) and OUT_DIR/detail.json (everything).
"""

import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

baseline_file, new_file, out_dir = sys.argv[1:4]
out_dir = Path(out_dir)
out_dir.mkdir(parents=True, exist_ok=True)

base = json.load(open(baseline_file, encoding="utf8"))
new = json.load(open(new_file, encoding="utf8"))


def key_items(items):
    """Key an equipment category list by tag, disambiguating collisions."""
    seen = Counter()
    out = {}
    for item in items:
        k = f'{item.get("tag")}|{item.get("dropsIn", "")}|{item.get("classification", "")}'
        seen[k] += 1
        if seen[k] > 1:
            k = f"{k}#{seen[k]}"
        out[k] = item
    return out


def collections(data):
    """
    Flatten the six top-level keys into {collection: {key: entry}}.

    Affixes are compared exactly as emitted: the order of `properties` and
    of the `equipment` CSV is part of the contract.

    """
    out = {}
    out["affixes.prefixes"] = data["affixes"]["prefixes"]
    out["affixes.suffixes"] = data["affixes"]["suffixes"]
    out["creatures"] = data["creatures"]
    for cat, items in data["equipment"].items():
        out[f"equipment.{cat}"] = key_items(items)
    out["quests"] = data["quests"]
    out["sets"] = data["sets"]
    out["skills"] = data["skills"]
    return out


def walk(a, b, path, changes):
    """Collect (path, old, new) leaf differences between a and b."""
    if isinstance(a, dict) and isinstance(b, dict):
        for k in sorted(set(a) | set(b)):
            p = f"{path}.{k}" if path else k
            if k not in a:
                changes.append((p, None, b[k]))
            elif k not in b:
                changes.append((p, a[k], None))
            else:
                walk(a[k], b[k], p, changes)
    elif isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b):
            changes.append((f"{path}[len]", len(a), len(b)))
        for i, (x, y) in enumerate(zip(a, b)):
            walk(x, y, f"{path}[{i}]", changes)
    elif a != b:
        changes.append((path, a, b))


def norm(path):
    """Collapse list indices to a field-shaped path."""
    return re.sub(r"\[\d+\]", "[]", path)


def short(v, n=90):
    s = json.dumps(v, ensure_ascii=False)
    return s if len(s) <= n else s[: n - 1] + "…"


bc = collections(base)
nc = collections(new)

summary = []
detail = {}
totals = Counter()

for coll in sorted(set(bc) | set(nc)):
    b = bc.get(coll, {})
    n = nc.get(coll, {})
    added = sorted(set(n) - set(b))
    removed = sorted(set(b) - set(n))
    common = sorted(set(b) & set(n))
    field_counts = Counter()
    examples = defaultdict(list)
    changed_entries = 0
    for k in common:
        changes = []
        walk(b[k], n[k], "", changes)
        if changes:
            changed_entries += 1
        for p, old, val in changes:
            fp = norm(p)
            field_counts[fp] += 1
            if len(examples[fp]) < 4:
                examples[fp].append({"key": k, "path": p, "old": old, "new": val})
    totals["added"] += len(added)
    totals["removed"] += len(removed)
    totals["changed"] += changed_entries
    detail[coll] = {
        "baseline": len(b),
        "new": len(n),
        "added": added,
        "removed": removed,
        "changed_entries": changed_entries,
        "fields": dict(field_counts.most_common()),
        "examples": examples,
    }

    def name(d, k):
        e = d.get(k, {})
        return e.get("name") if isinstance(e, dict) else None

    summary.append(f"## {coll}\n")
    summary.append(
        f"baseline {len(b)}, new {len(n)}, added {len(added)}, removed {len(removed)}, "
        f"changed {changed_entries}/{len(common)}\n"
    )
    if added:
        summary.append(
            "added: " + ", ".join(f"{k} ({name(n, k)})" for k in added[:25]) + ("…" if len(added) > 25 else "") + "\n"
        )
    if removed:
        summary.append(
            "removed: "
            + ", ".join(f"{k} ({name(b, k)})" for k in removed[:25])
            + ("…" if len(removed) > 25 else "")
            + "\n"
        )
    if field_counts:
        summary.append("\n| field | count | example (key: old -> new) |\n|---|---|---|\n")
        for fp, c in field_counts.most_common(40):
            ex = examples[fp][0]
            summary.append(f"| `{fp}` | {c} | {ex['key']}: {short(ex['old'])} -> {short(ex['new'])} |\n")
    summary.append("\n")

summary.insert(0, f"# diff {Path(baseline_file).name} -> {Path(new_file).name}\n\ntotals: {dict(totals)}\n\n")
(out_dir / "summary.md").write_text("".join(summary), encoding="utf8")
json.dump(detail, open(out_dir / "detail.json", "w", encoding="utf8"), ensure_ascii=False, indent=1)
print("".join(summary[:1]))
