import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
p = r".\STATE.md"
s = open(p, encoding="utf-8").read()
i = s.index("## 6. Files changed this session")
new = '''## 6. Files changed this session
- `server/stub_server.py` — `/quests/quest-begin`, `/quests/quest-movedir`
  (including the one-shot `currentBattleId + localPlayer` experiment).
- `server/data/quest_begin_response.json`, `quest_detail.json` — `entities`
  is now a dictionary keyed by entity id; top-level `scaledBossTable`; boss
  entity on (1,0).
- `spec/quest_protocol.md` — §2f: exact NRE instruction, `builder.summary.
  bossTable` chain, entity factory, `characters`, negative experiment.
- `LEDGER.md`, `FIDELITY.md`, `MASTER_PROMPT.md` — updated (v3.2).
- `OPEN_QUESTIONS.md` — author OneDrive link, battle-trigger gap, archive gaps.
- `COVERAGE_WIKI.md`, `archive/wiki/*.py`, `archive/wiki/README.md`,
  `data/wiki/README.md` — wiki archive and integrity state.
- `archive/wiki/meta/author_collection.json` — link, revid 10874, source.
- Work scripts: `disasm_calls.py`, `write_spec_2f.py`, `gen_coverage.py`,
  `find_tiles_arg.py`, `archive_wiki.py`.

## 7. Evidence index
- `work/r13.png` — BOTS roster.
- `work/r38.png` — quest detail with team, START active.
- `work/r47.png`, `work/r51.png` — quest map loaded.
- `work/r86.png`, `work/r95.png`, `work/r117.png` — boss entity rendered
  (6★, 8888) after the `entities` dictionary fix.
- `work/r119.png` — movedir accepted, bot stays at 11%, no
  `/matches/activate-match` after the `currentBattleId + localPlayer` attempt.
- `server/requests.jsonl` — request log; `05:41:47Z` is the negative attempt.
- `archive/wiki/state.json`, `manifest.json`, `errors.json` — archive integrity.
'''
open(p, "w", encoding="utf-8").write(s[:i] + new)
print("ok")
