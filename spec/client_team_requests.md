# Client team request shapes (RUN) — 2026-10-23/24

Extracted from `server/requests.jsonl` (all client requests observed during the
verified flow). This is what the client itself sends; the stub should echo the
same shape where the response is a team update.

## `/bcg/setSavedTeam`

Observed 62 times. Body:

```json
{
  "heroes": ["bumblebee_cin_dotm_2"],
  "api": 6,
  "nonce": "6adbd70f6911bc4d1e1c000c",
  "teamID": "0"
}
```

- `heroes`: **list of blueprint strings**, not objects.
- `teamID`: string (`"0"` in the observed flow).
- `api`/`nonce`: transport metadata.
- The client never sent `teamName`, `sid`, or a dictionary for this request.

Stub response should include a matching `updates.savedTeams` entry:

```json
{"sid": "0", "heroes": [{"bid": "bumblebee_cin_dotm_2", "rank": 1, "level": 1, "sig_lvl": 0, ...}]}
```

The current `/bcg/setSavedTeam` response already creates this list; the hero
details are `[ASSUMED]` computed values.

## `/quests/quest-begin/{qid}`

Observed 51 times. Body:

```json
{
  "quitExisting": true,
  "nonce": "6adbbb116911bc4d2b37000d",
  "hash": "v1",
  "api": 11,
  "setId": "story_act_1",
  "tm0": "bumblebee_cin_dotm_2"
}
```

- `setId` is the **quest set**, not the qid (`story_act_1` vs
  `story_act1_ch1_m1`).
- `tm0` is the first team member blueprint; `tm1..tm3` are not present for a
  one-bot team.
- `quitExisting: true` is sent even on the first begin.
- `hash` is `"v1"`.

Consequence: the response should expose an active team keyed by the mode
(`story`) and, for clients that use the set id, by `story_act_1`; the current
server also keeps qid/uniqueId aliases. The client's own `tm0` is the blueprint
to echo into the team details.

## `/bcg/getBaseHeroData`

Observed 33 times. Body:

```json
{
  "heroes": [{"level": 1, "sig_lvl": 0, "flvl": 0, "rank": 1, "bid": "enemy1"}],
  "nonce": "6adbd52c6911bc4d167b000e",
  "api": 6
}
```

- `heroes` is a list of **detail objects** (not strings).
- In the verified flow only `bid: "enemy1"` was requested; it is the battle
  enemy, not the player's team.
- Response is a JSON array of `BCGHeroDetails`.

## Team-related absence

No `/bcg/setActiveTeam` request was observed. The active team is created from
`setSavedTeam`/`quest-begin` data and the `activeTeams` collection.

## A1 mode

`ActiveQuest..ctor` (`0xC38BC8`) reads the quest dictionary and its `mode`
field; the live `ActiveQuest.mode` is `"story"` and `GetCurrentTeam` passes it
to `BCGHelper.GetActiveTeam` (`0xC1FFDC`). Accepted values observed/known:
`story` [RUN]; `pvp`, `arena`, `raid`, `ava`, `ave`, `base`, `special`,
`away` are candidate mode strings [STATIC/ASSUMED] and require a live request
to confirm. The lookup compares the string as-is; no case folding was found.
