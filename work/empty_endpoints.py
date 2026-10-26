"""List client-requested paths not covered by openapi (empty/fallback endpoints)."""
import json
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OPENAPI = json.loads((ROOT / "spec" / "openapi.json").read_text(encoding="utf-8"))
PATHS = set(OPENAPI.get("paths", {}))
REQ = ROOT / "server" / "requests.jsonl"
seen = Counter()
for line in REQ.read_text(encoding="utf-8", errors="replace").splitlines():
    try:
        d = json.loads(line)
    except Exception:
        continue
    p = d.get("path", "")
    p = re.sub(r"/[0-9a-f]{8,}", "/{id}", p)
    p = re.sub(r"/story_act[^/]+", "/{qid}", p)
    p = re.sub(r"/quests_fight", "/{matchType}", p)
    seen[p] += 1
missing = []
for p, n in seen.items():
    norm = p
    if norm not in PATHS and not any(norm.startswith(x.replace("{qid}", "").split("{")[0]) for x in PATHS):
        missing.append((n, p))
missing.sort(reverse=True)
lines = ["# Endpoints not covered / empty fallback (Step 8.3)", "",
         "Derived from `server/requests.jsonl` paths vs `spec/openapi.json`.",
         "These paths currently hit the `{}` fallback; client key expectations are",
         "`[ASSUMED]` until a capture shows the parsed fields.", "",
         "| count | path |", "|---:|---|"]
for n, p in missing[:60]:
    lines.append(f"| {n} | `{p}` |")
lines += ["", f"Total unmatched path patterns: {len(missing)}", "",
          "## Notes", "",
          "- Matching is approximate: numeric/id segments are normalized.",
          "- A path may be covered by a prefix route not listed as an exact openapi path.",
          "- Do not add guessed response keys; capture the client read with a breakpoint or",
          "  a known non-empty response first."]
(ROOT / "docs" / "empty_endpoints.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
print("missing", len(missing))
for n, p in missing[:12]:
    print(n, p)
