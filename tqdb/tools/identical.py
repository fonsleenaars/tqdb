"""
Parse one locale twice, in two processes, and fail unless the output is
byte-identical.

Python seeds its string hash per process, so anything the parser builds by
iterating a set comes out in a different order from one run to the next.
A single run cannot show that; two runs compared byte for byte can.

usage, from the repo root:

  docker compose run --rm -T dev uv run --frozen python tqdb/tools/identical.py [locale]

Exit status is 0 when the JSON output and sprite.css match, 1 otherwise.
"""
import hashlib
import subprocess
import sys
from pathlib import Path

# Run as a script, so the repo root is not on the path by itself.
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from tqdb import __version__  # noqa: E402

locale = sys.argv[1] if len(sys.argv) > 1 else "en"
files = [Path("output") / f"tqdb.{locale}.{__version__}.json", Path("output") / "sprite.css"]


def run():
    subprocess.run([sys.executable, "run.py", "--locale", locale], check=True)
    return {f: hashlib.sha256(f.read_bytes()).hexdigest() for f in files}


first = run()
second = run()
for f in files:
    print(f"{f}: {'identical' if first[f] == second[f] else 'DIFFERS'}")
sys.exit(0 if first == second else 1)
