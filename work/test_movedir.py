import urllib.request, json
req = urllib.request.Request(
    "http://127.0.0.1:8080/quests/quest-movedir/story_act1_ch1_m1/1/0",
    data=b'{"api":11,"nonce":"x"}',
    headers={"Content-Type": "application/json"},
)
d = json.load(urllib.request.urlopen(req))
print(json.dumps(d, ensure_ascii=False, indent=1)[:2000])
