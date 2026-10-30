import json
import os
from collections import Counter

import UnityPy

ASSETS = "work/unpacked/assets"
ASSETPACK = os.path.join(ASSETS, "assetpack")

ids = []
for d in sorted(os.listdir(ASSETPACK)):
    if not d.endswith("_odr"):
        continue
    base = d[:-4]
    if os.path.exists(os.path.join(ASSETPACK, d, base + ".assetbundle")):
        ids.append(base)

# merged-only bots from the main characters bundle
ids += ["starscream_gs", "optimusprime_gs_v"]

out = {"bundles": {}, "counts": {}}
extra = [
    "characters/characters.assetbundle",
    "characters/moves.assetbundle",
    "characters/character_audio.assetbundle",
    "characters/character_fx.assetbundle",
    "characters_procedural_odr/character_mergecharacters_procedural.assetbundle",
]
paths = []
for bid in ids:
    p = os.path.join(ASSETPACK, bid + "_odr", bid + ".assetbundle")
    if os.path.exists(p):
        paths.append((bid, p))
    else:
        paths.append((bid, os.path.join(ASSETPACK, "characters", "characters.assetbundle")))
for rel in extra:
    paths.append((rel.split("/")[-1].replace(".assetbundle", ""), os.path.join(ASSETPACK, rel)))

seen = set()
for name, path in paths:
    if path in seen:
        continue
    seen.add(path)
    if not os.path.exists(path):
        out["bundles"][name] = {"path": path, "missing": True}
        continue
    try:
        env = UnityPy.load(path)
        counts = Counter(o.type.name for o in env.objects)
        gos, clips, monos = [], [], []
        for o in env.objects:
            t = o.type.name
            if t not in ("GameObject", "AnimationClip", "MonoBehaviour"):
                continue
            try:
                d = o.read()
                n = getattr(d, "m_Name", "") or ""
            except Exception:
                n = ""
            if not n:
                continue
            if t == "GameObject":
                gos.append(n)
            elif t == "AnimationClip":
                clips.append(n)
            else:
                monos.append(n)
        out["bundles"][name] = {
            "path": path.replace("\\", "/"),
            "bytes": os.path.getsize(path),
            "types": dict(counts),
            "gameobjects": sorted(set(gos)),
            "animation_clips": sorted(set(clips)),
            "monobehaviours": sorted(set(monos))[:80],
        }
        print("ok", name, len(gos), len(clips), flush=True)
    except Exception as e:
        out["bundles"][name] = {"path": path, "error": repr(e)}
        print("ERR", name, e, flush=True)

out["counts"] = {
    "bot_bundles": len(ids),
    "bundles_read": sum(1 for v in out["bundles"].values() if "error" not in v and "missing" not in v),
}
open("work/bundle_inventory.json", "w", encoding="utf-8").write(
    json.dumps(out, ensure_ascii=False, indent=1))
print("wrote", out["counts"])
