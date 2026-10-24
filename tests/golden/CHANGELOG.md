# Golden regression changelog

## 2026-10-24 re-record

Previous baseline: git tag `golden-baseline-2026-10-23` (commit `0d0641c`).
New baseline: current `expected_shapes.json`.

Changed requests (recursive shape diff in `diff_2026-10-24.json`):

| Request | Change | Reason |
|---|---|---|
| `/bcg/getLoginData` | 57 new `result.blueprints.*` keys | R1 59-bot catalog grant (deliberate test roster) |
| `/quests/quest-movedir/story_act1_ch1_m1/1/0` | `result.teamData.updates.activeTeams.story_act_1` added | client sends `setId=story_act_1`; server exposes an aliased active team so the quest-detail/prefight lookup can use it |
| `/quests/quest-list` | no recursive shape change; values now use `showUI`/`group`/`recommendMinLevel` | correct wire keys (the shape is only key/type level; values are not in the golden) |

No other request shape changed. This re-record is intentional and is
referenced in `LEDGER.md` §21. Re-record only with a written reason.
