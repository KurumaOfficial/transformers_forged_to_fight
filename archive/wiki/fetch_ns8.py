import sys, time, json
sys.path.insert(0, r"C:\Users\gameg\Desktop\TFTF\archive\wiki")
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import archive_wiki as aw
base = aw.WIKIS["fandom"]
titles = [x["title"] for x in json.load(open(r"C:\Users\gameg\Desktop\TFTF\archive\wiki\meta\allpages_fandom_8.json", encoding="utf-8"))]
end = time.time() + 120
for t in titles:
    print("fetch", t)
    aw.fetch_page(base, "fandom", t, 8, end)
    aw.fetch_html(base, "fandom", t, 8, end)
    time.sleep(0.5)
print("done", len(titles))
