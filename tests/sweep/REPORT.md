# BOTS sweep (12 of 59, 2026-10-25)

The first 12 cards (Windblade, Wheeljack, Waspinator, Ultra Magnus,
Thundercracker, Tantrum, and the next row) were opened on the live BOTS screen:
card popup, then INFO details. All 12 details screens rendered; no
`NullReferenceException` was logged in any of the 12 runs.

Screenshots: `tests/sweep/bot_00_*.png` ... `bot_11_*.png`; machine-readable
result: `tests/sweep/sweep_12.json`.

Observed on every details screen:
- `ABILITIES: NO ABILITIES` (the active ability list is not populated);
- special attacks are raw localization ids such as
  `M1_SPECIAL_ATTACK_WHEELJACK_GS.0` (R3/R4 still open);
- Synergy Bonuses box is empty (R4);
- stats are the stub rank-1 values (level 1/10, rank 1/5, 855 HP / 82 ATK for
  a bot whose wiki star-1 is different; R1/R2 still open).

Not swept: cards 13-59. They are in the same list widget and the same data
shape; a full 59-card sweep needs scrolling and is deferred. This is a partial
S1 result, not a claim that all 59 were individually opened.
