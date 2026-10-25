"""Read-only audit of large unreachable objects in .git/objects."""
import hashlib
import os
import subprocess
import sys
import zipfile
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GIT = "git"
sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def sh(*args, timeout=120):
    return subprocess.run([GIT] + list(args), cwd=str(ROOT), capture_output=True, timeout=timeout)


def oid_of(path: Path):
    h = path.parent.name
    return h + path.name


def blob_head(oid, n=16):
    p = subprocess.Popen([GIT, "cat-file", "-p", oid], cwd=str(ROOT), stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    data = p.stdout.read(n)
    p.kill()
    return data


def zip_names(oid, tmp: Path):
    with tmp.open("wb") as f:
        p = subprocess.Popen([GIT, "cat-file", "-p", oid], cwd=str(ROOT), stdout=f, stderr=subprocess.DEVNULL)
        p.wait(timeout=600)
    try:
        with zipfile.ZipFile(tmp) as z:
            return z.namelist()[:12], len(z.namelist())
    except Exception as exc:
        return [f"not a zip: {exc}"], 0


def main():
    objs = []
    for p in (ROOT / ".git" / "objects").glob("*/*"):
        if not p.is_file() or p.name.startswith("tmp_"):
            continue
        objs.append((p.stat().st_size, p))
    objs.sort(reverse=True)
    out = []
    for size, p in objs[:20]:
        if size < 1024 * 1024:
            continue
        oid = oid_of(p)
        typ = sh("cat-file", "-t", oid).stdout.decode().strip()
        head = blob_head(oid, 12)
        rec = {
            "oid": oid,
            "bytes": size,
            "mtime_utc": datetime.fromtimestamp(p.stat().st_mtime, timezone.utc).isoformat(),
            "type": typ,
            "head_hex": head.hex(),
            "head_ascii": "".join(chr(b) if 32 <= b < 127 else "." for b in head),
            "sha256": None,
            "zip_names": None,
            "zip_entries": None,
        }
        if typ == "blob" and head[:2] == b"PK":
            tmp = ROOT / "work" / "dangling_tmp.zip"
            try:
                names, count = zip_names(oid, tmp)
                rec["zip_names"] = names
                rec["zip_entries"] = count
            finally:
                tmp.unlink(missing_ok=True)
        if size <= 200 * 1024 * 1024:
            h = hashlib.sha256()
            p2 = subprocess.Popen([GIT, "cat-file", "-p", oid], cwd=str(ROOT), stdout=subprocess.PIPE,
                                  stderr=subprocess.DEVNULL)
            while True:
                chunk = p2.stdout.read(1024 * 1024)
                if not chunk:
                    break
                h.update(chunk)
            p2.wait()
            rec["sha256"] = h.hexdigest()
        out.append(rec)
    import json
    (ROOT / "work" / "git_dangling.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    for r in out:
        print(r["bytes"], r["oid"], r["type"], r["head_ascii"], r.get("zip_entries"), r.get("zip_names"))


if __name__ == "__main__":
    main()
