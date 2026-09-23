# SMC chart validation — 18 September 2026

## 23 September 2026 — v1.4 pullback-continuation revision

- Added the separate HTF pullback-continuation model, full-session/any-time window options, internal hidden-zone calculation and a two-signal default quota.
- The earlier sweep-reversal model remains selectable and retains its opening-window sequence.
- Local rule fixtures and source guards pass for bearish supply rejection, countertrend rejection, confirmed-bar zone age, quota reset and sweep-model independence.
- This revision has **not yet been compiled or replayed in TradingView**. The older live-compilation results below apply only to the exact earlier sources and must not be presented as validation of v1.4.

## v1.1 session-candidate update (08:23 SAST)

- Final source SHA-256: `2d5d919360a0d7057d07b469ce7ddd01fafecffe91d17dc6cd56081d679c1c19`.
- Readback matched local source before compilation. Final revision compiled, updated on chart and saved privately as SMC Context Companion v1.1 (chart title SMC Sessions).
- The prior account's SMC source was not editable in the new account. Its existing instance was preserved and hidden; a new private copy was created. ORB instances and source files were untouched.
- Both new toggles were enabled and recalculated successfully. The faint adjustable start-bar highlight was visually observed in replay.
- Diagnostic replay used a deliberately nonstandard London 00:00 local start, 120-minute window, Unfiltered direction, 24-bar setup lifetime and 2-ATR invalidation buffer to exercise candidate creation. A single LDN possible buy box was observed at the replay endpoint around 02:20 SAST on 18 September. These were software-path tests, NOT proposed trading settings or evidence of an edge.
- Found and fixed duplicate candidate/ordinary-OB captions at identical bounds. Recompiled the exact revised source, then visually verified the single LDN possible buy caption without the duplicate OB caption.
- Restored London 08:00, NY 08:00, 60 minutes, Both HTFs agree, 12 bars, 0.1 ATR. Both feature toggles remain ON; minimal start-bar highlighting selected. Other inputs use the new copy's clean source defaults; the older customized overlay remains hidden and unchanged.
- Returned to live M5 without saving the disposable replay. Thirty local source guards and independent semantic fixtures passed, including DST/window boundary checks and ORB source integrity.
- This is a limited candidate-rendering/recalculation smoke test. Candidate touch/expiry combinations have not all been visually stepped through in TradingView. No profitability claim, full HTF-POI validation, trade execution or alert activation.

## Scope and results

- 17 September: exact local Pine source pasted into a new TradingView editor; clipboard readback matched the local source after newline normalization. Compiled, added and privately saved as SMC Context Companion v1. No compiler error was observed.
- Source SHA-256 at compilation: `0ff2c30fe641520aacc42c36922e9ed2578f2899a5678576d03a8fa0e7264bb8`.
- Feed: FXCM `FX:XAUUSD`, M5 hollow candles (standard OHLC presentation), chart timezone UTC+2. This is not the OANDA feed shown in some earlier user screenshots.
- CHoCH, sweeps, a supply OB and the H1/H4 context caption rendered. BOS/FVG options were exercised and recalculated without a displayed runtime error. The indicator menu reported its scale as right, matching the chart's visible price scale.
- Intraday replay was initially blocked by the first account's plan. No upgrade was purchased.
- 18 September: retried after the user switched accounts. Replay successfully loaded a morning endpoint around 04:45 SAST and advanced through approximately 05:35. Observed a new Low swept mark, then a BOS down mark, followed by recovery candles; zones and the latest range updated. No runtime error appeared during this short sequence.
- Dragging the chart during replay kept event marks aligned with their candles. The single context label can clip at the right edge when little future space is available; moving the chart left made it readable.
- The latest context in the inspected replay sequence was H1 bullish / H4 bearish, correctly presented as mixed. The new account's existing custom settings included BOS, FVGs, range shading and an H1 range; these were preserved rather than reset.
- Returned to live M5, leaving SMC visible and both existing ORB scripts hidden as found. ORB source and input rules were not changed. No trades or alerts were created. The disposable replay was exited without saving a separate replay session.
- Re-ran 24 local source-guard / independent rule-model tests: all passed, including ORB source-integrity checks.

## Limits and useful follow-up

This is a compilation and execution smoke test, not a performance backtest, a full price-by-price audit, or proof of non-repainting across all data/reload cases. Existing on-chart source was carried across the account switch; it was not independently re-exported on the second account. A longer replay around a specific ORB signal would be needed to assess the context available at that signal.

The algorithm remains a latest-confirmed-pivot SMC approximation, not a verified reproduction of the supplied creators' protected-swing/inducement methods. H1/H4 direction and range are higher-timeframe context; OB/FVG zones are chart-timeframe zones. Current context must not be applied retrospectively to earlier signals.

Visual observations: distant HTF range boundaries can compress M5 candles under autoscaling; the range display can be switched off without removing H1/H4 direction. Dense BOS/sweep settings can crowd event labels. Neither is evidence that an ORB signal is automatically invalid.
