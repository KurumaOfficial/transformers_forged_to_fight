# Endpoints not covered / empty fallback (Step 8.3)

Derived from `server/requests.jsonl` paths vs `spec/openapi.json`.
These paths are not exact openapi entries; movedir has a prefix handler,
`__control` is the experiment control, and the rest may hit the `{}` fallback.
Client key expectations are `[ASSUMED]` until a capture shows the parsed
fields.

| count | path |
|---:|---|
| 119 | `/quests/quest-movedir/{qid}/1/0` |
| 17 | `/quests/quest-movedir/{qid}/0/1` |
| 8 | `/quests/quest-quit/{qid}` |
| 5 | `/__control` |
| 4 | `/invites/privacy` |
| 1 | `/kabamsignup/signup/never` |
| 1 | `/kabamsignup/signup/later` |
| 1 | `/benchmark/performance` |
| 1 | `/bcg/getHeroXPCurve` |
| 1 | `/account` |
| 1 | `/` |

Total unmatched path patterns: 11

## Notes

- Matching is approximate: numeric/id segments are normalized.
- A path may be covered by a prefix route not listed as an exact openapi path.
- Do not add guessed response keys; capture the client read with a breakpoint or
  a known non-empty response first.
