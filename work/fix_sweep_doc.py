from pathlib import Path

p = Path("docs/sweep_diagnosis.md")
s = p.read_text(encoding="utf-8")
start = s.index("Page hashes changed")
end = s.index("Result file:", start)
end2 = s.index("\n", end)
new = (
    "Page hashes changed, but the page screenshots `tests/sweep/page_01..04.png`\n"
    "show the **same first 12 cards** (`Windblade..Tantrum`). The hash change is\n"
    "a transition/popup artifact, not proof of pagination. The BOTS grid is a\n"
    "**vertical scroll**; the horizontal-swipe sweep does not visit the other\n"
    "cards. Therefore `info_error=0` for 59 rows is **not** proof of 59 distinct\n"
    "bots. Fix: scroll down with `input swipe 1200 900 1200 300 400`, capture the\n"
    "new rows, and rerun. The old 59/59 report is historical, not coverage\n"
    "evidence. Result file: `tests/sweep/sweep_59.json`."
)
p.write_text(s[:start] + new + s[end2:], encoding="utf-8")
print("ok")
