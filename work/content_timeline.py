"""4.1 content timeline: saved page revisions vs APK 2022-07-26 / close 2023-01-13."""
import json
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGES = json.loads((ROOT / "data" / "wiki" / "pages.json").read_text(encoding="utf-8"))["pages"]
APK = datetime.fromisoformat("2022-07-26T00:00:00+00:00")
CLOSE = datetime.fromisoformat("2023-01-13T23:59:59+00:00")
OUT = ROOT / "docs" / "content_timeline.md"

rows = []
for name, p in PAGES.items():
    src = p.get("source") or {}
    ts = src.get("timestamp")
    try:
        dt = datetime.fromisoformat(ts.replace("Z", "+00:00")) if ts else None
    except Exception:
        dt = None
    if dt:
        rows.append((dt, name, src.get("revid"), p.get("lead", "")[:120]))
rows.sort()
post_apk = [r for r in rows if r[0] >= APK]
between = [r for r in rows if APK <= r[0] <= CLOSE]
after_close = [r for r in rows if r[0] > CLOSE]

lines = ["# Content timeline (Step 4.1)", "",
         "APK 9.2.0 date: **2022-07-26**; target shutdown: **2023-01-13**.",
         "Timestamps are the **saved wiki revision** timestamps, not necessarily",
         "the first-ever revision or the in-game release date. Treat in-game dates",
         "as `[ASSUMED]` unless the page text states them.", "",
         f"- pages with timestamp: {len(rows)}",
         f"- saved revision >= APK: {len(post_apk)}",
         f"- APK..close: {len(between)}",
         f"- after close: {len(after_close)}", "",
         "## Pages whose saved revision is at/after the APK", "",
         "| saved date | page | revid | note |", "|---|---|---:|---|"]
for dt, name, revid, lead in post_apk[:80]:
    lines.append(f"| {dt.date()} | {name} | {revid} | {lead.replace('|','/')[:100]} |")
lines += ["", "## Specific content named in the queue", ""]
for needle in ["Starscream", "Chromia", "Dead End", "Soundblaster", "Awaken and Corrupt",
               "Autobots Turn", "Decepticons Burn"]:
    hit = [r for r in rows if needle.lower() in r[1].lower()]
    if hit:
        for dt, name, revid, _ in hit[:5]:
            lines.append(f"- `{name}`: saved revision {dt.date()} (revid {revid})")
    else:
        lines.append(f"- `{needle}`: no page timestamp in `pages.json`")
lines += ["", "## Interpretation", "",
          "- Pages saved after the APK date are candidates for post-9.2.0 content,",
          "  but a late save does not prove a late release (old pages are re-saved).",
          "- Starscream has a page but no 9.2.0 pack; Act 4 I/II and the extra bots",
          "  are the strongest post-APK candidates and must be checked against the",
          "  page text/release notes, not only the saved timestamp.",
          "- For missing packs, the correct action is a later APK/asset pack or an",
          "  explicit `[ASSUMED]` fallback; do not invent a 9.2.0 pack.",
          ]
OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
print("pages", len(rows), "post_apk", len(post_apk), "after_close", len(after_close))
for r in post_apk[:10]:
    print(r[0].date(), r[1])
