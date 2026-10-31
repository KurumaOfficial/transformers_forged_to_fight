import urllib.request, re, sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
u = "https://1drv.ms/u/s!ApD2f3dIXZ_7yjf4KMB9YQzgWQCG?e=jiLxKN"
req = urllib.request.Request(u, headers={"User-Agent": "TFTF-offline-archive/0.1"})
h = urllib.request.urlopen(req, timeout=60).read().decode("utf-8", "replace")
print("len", len(h))
print("auth", re.findall(r"isAuthenticated\"?:\s*([a-z]+)", h)[:5])
print("downloadUrl", len(re.findall(r"downloadUrl", h)))
print("png", len(re.findall(r"\.png", h, re.I)), "jpg", len(re.findall(r"\.jpg", h, re.I)))
print(h[:600])
