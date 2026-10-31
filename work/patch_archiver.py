from pathlib import Path
p = Path(r".\archive\wiki\archive_wiki.py")
s = p.read_text(encoding="utf-8")
s = s.replace(
    'ap.add_argument("--minutes", type=float, default=10)',
    'ap.add_argument("--minutes", type=float, default=10)\n    ap.add_argument("--wiki", default="all", choices=["all", "fandom", "tfwiki"])',
)
s = s.replace(
    'for wiki, base in WIKIS.items():\n        if args.phase',
    'for wiki, base in WIKIS.items():\n        if args.wiki != "all" and wiki != args.wiki:\n            continue\n        if args.phase',
)
p.write_text(s, encoding="utf-8")
print("ok")
