from pathlib import Path
p = Path(r".\work\parse_bots.py")
s = p.read_text(encoding="utf-8")
s = s.replace(
    'pat = re.compile(r"(?ms)^==+\\s*" + re.escape(heading) + r"\\s*==+\\s*(.*?)(?=^==+\\s*[^=\\n]|\\Z)")',
    'pat = re.compile(r"(?ms)^==(?!=)\\s*" + re.escape(heading) + r"\\s*==\\s*(.*?)(?=^==(?!=)\\s*[^=\\n]|\\Z)")',
)
s = s.replace(
    'm = re.search(r"(?is)\\{\\{Infobox_character(.*?)\\n\\}\\}", text)',
    'm = re.search(r"(?is)\\{\\{Infobox_character(.*?)\\}\\}", text)',
)
p.write_text(s, encoding="utf-8")
print("patched parser")
