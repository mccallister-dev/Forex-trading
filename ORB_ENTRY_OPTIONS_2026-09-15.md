# Entry-options correction — 15 September 2026

Implemented in the separate Strategy Tester strategy and manual-signal indicator. Original v1 strategy and framework indicator are unchanged. Pre-change copies are in `Backups/2026-09-15-before-entry-options/`.

## Behavior

| Entry model | Signal confirmation |
|---|---|
| Close breakout | Qualifying fresh breakout candle close; no retest or continuation required. |
| Break + retest | Later qualifying retest/rejection candle close; no continuation required. |
| Break + retest + continuation | Breakout, later qualifying retest, then another candle beyond both extremes. |

Context Off/Required and entry delay are independent controls. All modes retain the complete ORB, displacement, direction, trend, stop-distance and one-signal-per-session guards. This restores trigger choices, not exact v1 behavior. Continuation/Required remains the default for continuity, not because it has been proven most effective.

A close breakout before the minimum delay is not queued for a later entry. The retest-close model requires an eligible retest at/after the delay; it does not issue a stale retest signal when time alone advances. Context for close breakout can count previously confirmed OB/FVG touches, but not a retracement of its own newly formed impulse. Retest Fib behavior is unchanged. Pullback-extreme stop uses the breakout candle extreme when no retest is required.

Manual plans still remain active until an SL/TP level is touched. No session-end plan expiry or real broker orders were introduced. Alert activation is not required for chart signals. Both scripts must have matching inputs to compare their signal engines; simulated fills and position handling can still differ from manual plans.

## Verification

- Generator `--check`: passed for both standalone Pine files.
- All 21 source, data and formula unit tests passed. These are not a Pine interpreter or an exhaustive behavioral backtest.
- Both revised scripts were compiled and updated on the signed-in TradingView chart on 15 September 2026. The first manual editor insertion left residual text and produced a compilation error; it was replaced with the full verified source, then successfully recompiled. No compilation error remained.
- Clipboard readback after LF normalization matched the expected character counts and FNV-1a fingerprints: strategy 32,627 / `c5d1ad43`; manual 34,581 / `fea62b18`. Manual readback also matched the complete submitted text exactly. Local SHA256 identities are below.
- Strategy regression: FXCM EURUSD, M15, London 09:00–17:00 SAST, both directions, 30-minute ORB, zero profile delay, required context count 2, opposite-ORB stop, 1% risk, 3R. The visible report window was 30 June–15 September 2026. Revised continuation reproduced the pre-change 6 closed trades, 3 winners, +ZAR 610.96 net PnL, profit factor 2.932 and ZAR 259.23 maximum drawdown.
- Execution smoke checks on the same chart: Close breakout / Context Off produced 35 closed trades, +ZAR 2,244.82, PF 1.950; Break + retest / Context Off produced 22 closed trades, +ZAR 1,904.00, PF 2.404. These are recorded to identify executed test cases, not as a strategy ranking. Context differs from the regression control, samples are small, and broker costs were not validated. No new Gold performance claim follows from these checks.
- Manual visual check: Close breakout / Context Off with the profile-timeframe requirement temporarily disabled displayed BUY captions naming Close breakout, estimated entry/SL/TP, 3R and Context Off. All test input changes were restored afterwards.
- No live notification delivery, broker sizing convention, exhaustive edge cases, out-of-sample robustness, or Gold/multi-pair profitability was validated in this correction.

The chart has both the manual and strategy script visible, so their top-right panels overlap. Hide one script or turn off its Show status panel input when inspecting the other. Settings were restored after testing: strategy continuation/Required, both directions, profile-timeframe requirement off; manual continuation/Required, Profile direction, profile-timeframe requirement on. On EURUSD M15 the latter requirement prevents manual signals because its Auto profile expects M5. Disable that guard intentionally when comparing another timeframe.

## Source identities

| File | SHA256 |
|---|---|
| `tools/orb_v3_core.pine.inc` | `10a666761a532612f916d8cea5e79cacb6535d20d992eb42fd20dc99047cffe2` |
| `ORB_ICT_Manual_Signals_v3.pine` | `932ecb67e81bdc4fb860c65070f95188895fd005efa68452223738ac657c1a49` |
| `ORB_ICT_Backtest_Strategy_v2.pine` | `859072317149ee9d63abf63c62a55aa73c8e9d00ccc84bab50d68811bc2b8115` |

Edit the shared engine/tails and regenerate with `tools/build_orb_v3.py`; do not independently edit the two generated files. See `ORB_V3_SETUP_GUIDE.md` for entry timing, 10,000 ZAR capital, 0.2% margin for 500:1 leverage, and export instructions.
