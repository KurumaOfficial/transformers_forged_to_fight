"""Build docs/content_release_dates.md from the saved wiki infoboxes."""
import json
import re
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BOTS = json.loads((ROOT / "data" / "wiki" / "bots.json").read_text(encoding="utf-8"))["bots"]
OUT = ROOT / "docs" / "content_release_dates.md"
APK = datetime(2022, 7, 26)


def parse_date(raw):
    if not raw:
        return None
    s = str(raw)
    m = re.search(r"([A-Z][a-z]+ \d{1,2}(?:st|nd|rd|th)?, \d{4})", s)
    if m:
        s = m.group(1)
    else:
        s = s.split("|")[0].strip()
    s = s.replace("(Netflix)", "").replace("(update)", "").replace("(Bot)", "").strip()
    s = re.sub(r"(\d+)(st|nd|rd|th)", r"\1", s)
    for fmt in ("%B %d, %Y", "%b %d, %Y", "%Y-%m-%d", "%d %B %Y"):
        try:
            return datetime.strptime(s, fmt)
        except ValueError:
            pass
    m = re.search(r"(\d{4})", s)
    if m:
        try:
            return datetime(int(m.group(1)), 1, 1)
        except ValueError:
            pass
    return None


rows = []
for name, data in BOTS.items():
    raw = ((data.get("infobox") or {}).get("Release Date") or "").strip()
    dt = parse_date(raw)
    rows.append((dt or datetime(1900, 1, 1), name, raw, dt is not None and dt >= APK))

rows.sort(key=lambda r: (r[0], r[1]))
post = [r for r in rows if r[3]]
launch = [r for r in rows if r[2].startswith("Launch")]

lines = [
    "# Bot release dates from the saved wiki infoboxes (Step 4)",
    "",
    "Source: `data/wiki/bots.json`, `infobox.Release Date` (44/44 bots have the",
    "field). APK date: **2022-07-26**. A date after that is a post-APK content",
    "candidate; it is not proof that the 9.2.0 client can load the bot.",
    "",
    f"- non-Launch dates parsed: **{sum(1 for r in rows if r[2] and not r[2].startswith('Launch'))}**",
    f"- `Launch`: **{len(launch)}**",
    f"- no date: **{sum(1 for r in rows if not r[2])}**",
    f"- post-APK candidates: **{len(post)}**",
    "",
    "## Post-APK candidates",
    "",
    "| bot | release date (raw) | parsed |",
    "|---|---|---|",
]
for dt, name, raw, is_post in post:
    lines.append(f"| {name} | {raw} | {dt.date().isoformat()} |")

lines += [
    "",
    "## All bots",
    "",
    "| bot | release date (raw) | parsed | post-APK |",
    "|---|---|---|---|",
]
for dt, name, raw, is_post in rows:
    parsed = "" if dt.year == 1900 else dt.date().isoformat()
    lines.append(f"| {name} | {raw} | {parsed} | {'yes' if is_post else ''} |")

lines += [
    "",
    "## What this changes",
    "",
    "- **Starscream** has `August 24, 2017`: the bot is pre-APK, so the",
    "  \"Starscream is post-APK\" claim is **not supported by the infobox**. The",
    "  9 missing boss ids/pack are a separate mapping gap, not a release-date",
    "  gap.",
    "- **Sunstreaker** (`July 27, 2022 (update)`, `August 11, 2022 (Bot)`) is",
    "  the clearest post-APK bot.",
    "- **Soundblaster/Tactician** has `September 15th, 2022`; the base",
    "  Soundblaster page says `May 10, 2023`, which is the Netflix-era page.",
    "- **Chromia and Dead End** say `May 10, 2023`, i.e. after the 2022-07-26",
    "  APK and after the 2023-01-13 shutdown; they are not in the 9.2.0 pack.",
    "- Missions/events still need the same per-page treatment; their saved",
    "  revision dates are not release dates. `docs/content_timeline.md` has the",
    "  current partial list.",
]
OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
print("wrote", OUT, "post", len(post), "launch", len(launch))
