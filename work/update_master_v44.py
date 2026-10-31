from pathlib import Path

p = Path(r".\MASTER_PROMPT.md")
s = p.read_text(encoding="utf-8")
i = s.find("**P0 A:**")
j = s.find("## Next queue", i)
new = """**P0 A:** A1 **done**; A2 **done**; A3 **done**; A4 **done**; A5 **done**; A6 **done**; A7 **done**; A8 **done**; A9 **partial/blocked** (activate-match captured; model-id/tags fixed; `PlayerAttributes.Init` HashSet NRE; no match-loaded); A10 plan only.
**P0 S:** S1 **partial** (12/59; emulator stability); S2 **done**.
**P1 I:** I1/I2 **done**.
**P1 R:** R1 **partial** (LOBO: 14.3%/16.4% without anchor, 4.1%/2.8% with one anchor; 37 table-anchored `[DERIVED]`, rest `[ASSUMED]`); R2 **partial** (fit, not formula); R3 **blocked** (no text source; raw ids); R4 **partial** (synergy data added, unverified; specials raw); R5 **done**; R6 **partial** (switch implemented, original flow unverified).
**P1 Q:** Q1/Q2/Q3 **done** (90 missions; detail/begin/movedir dynamic; maps/boss map); Q4/Q5 **blocked** (battle doesn't finish; static docs).
**P1 C:** C1 **partial**; C2 **partial**; C3 **partial** (4 verified); C4 **done**.
**P1 W:** W1 **partial** (2/36 priority recovered, 34 blocked); W2-W4 **partial** (extracts + gaps); W5 **done**.
**P2 T:** T1 **partial** (payloads dynamic, routing still central); T2 **done**; T3 **done**; T4 **done**; T5 **done**.
**Step 0:** git audit **done**; **no push/remote changes**; cleanup plan pending user decision.
**Step 1:** windowed `angle_indirect` stable so far; watchdog not yet written.

## Next queue (v4.5)

1. Battle: breakpoint on `0xDAC198`/`HashSet..ctor` to identify the null collection; then match-loaded/resolve.
2. Step 1: `work/emulator_watchdog.py` + snapshots + smoke integration.
3. S1 59/59; R3/R4; Q4/Q5 after battle.
4. C1/C2/C3 deeper; W2 exact economy; W1 remaining priority URLs.
5. T1 route split; git cleanup only after user decision.

"""
s = s[:i] + new + s[j:]
p.write_text(s, encoding="utf-8")
print("replaced")
