# ORB research and test plan — 14 September 2026

Historical report: the root Pine files were revised on 15 September to add independent Close breakout, Break + retest, and continuation entry choices. The results and source identities below describe the earlier versions, not a fresh validation of the revised modes. See [revision validation](../ORB_ENTRY_OPTIONS_2026-09-15.md) and [current setup guide](../ORB_V3_SETUP_GUIDE.md).

The exports identify **research candidates**, not a reliably profitable pair or a validated 45–55% win rate. The new tools deliberately separate manual signals from simulated orders. Originals are unchanged; dated copies are in `Backups/2026-09-14-before-manual-v3`.

## What the results support

44 Strategy Tester workbooks contain 41 distinct runs across seven instruments. Three XAUUSD pairs of exports repeat the same settings and trades: (6)/(9), (7)/(10), and (8)/(11). They are not independent confirmations. Every workbook's closed-trade count and net profit reconciled to its summary within cent-level rounding. Five workbooks include an open trade; these are excluded from closed-trade statistics, not counted as wins or losses.

All runs used ZAR 10,000 initial capital, 10% equity risk, 500x leverage, a 30-minute ORB, a 2.75R target, zero commission and one tick of slippage. These costs are placeholders, not a verified broker model. Session-end exits were enabled in 33/44 files, so actual winning/losing amounts often differed substantially from +2.75R/−1R. Across timeframes, the available history changes: generally late July onward on M5, April onward on M15, January onward on M30. Full-period net profits are therefore not an apples-to-apples ranking.

### Candidates to test first

These are the **old v1 results**, not results for the new context-filtered engine. Profit factor below is gross winning ZAR divided by absolute gross losing ZAR. Drawdown is the workbook's intrabar percentage, at its unusually high 10% risk.

| Candidate | Old entry model | Closed trades | Win rate | Profit factor | Max drawdown | Interpretation |
|---|---|---:|---:|---:|---:|---|
| EURUSD M5, London, long | Close breakout | 21 | 57.1% | 1.82 | 28.56% | Promising small sample; test both-direction control too. |
| GBPJPY M5, London, short | Close breakout | 17 | 64.7% | 2.34 | 30.10% | Strongest small-sample lead, not a dependable win-rate estimate. |
| GBPJPY M5, London, both | Break + retest | 24 | 45.8% | 1.78 | 37.09% | Useful less direction-restricted alternative. |
| GBPUSD M5, London, both | Break + retest | 20 | 45.0% | 1.47 | 39.88% | Worth testing; M15 retest was weak over its longer period. |
| XAUUSD M15, New York, short | Break + retest | 33 | 45.5% | 1.44 | 45.53% | Gold research candidate, with substantial drawdown and timing uncertainty. |
| XAUUSD M30, New York, short | Break + retest | 36 | 55.6% | 1.58 | 43.58% | Looks better over its full history, but weaker in the recent common window. |

Source files are identifiable by pair/timeframe/direction/model in `run_comparison.csv`; XAUUSD M15 short is (7)/(10), M30 short is (8)/(11), EURUSD M5 long is (3), GBPJPY M5 short is the unsuffixed file, GBPJPY M5 retest is (4), and GBPUSD M5 retest is (3).

To reduce compounding distortion, I also divided each trade's PnL by its estimated pre-entry risk budget: `PnL / (reconstructed pre-entry equity × 10%)`. This is **budget-normalized PnL, not exact realized R**; gaps, conversion, rounding, caps and execution can change the actual amount at risk. It is not a replay at 1% risk.

On the overlapping dates within each pair, XAUUSD M15 short has budget-normalized PF 1.27 over 11 trades, versus M30 short PF 0.54 over 11. EURUSD M5 long is 2.13 over 21; GBPJPY M5 short 2.92 over 17; GBPUSD M5 both-direction retest 1.67 over 20. These small, selected samples justify research priorities, not a cross-pair investment ranking. Other inputs still differ between configurations. Trades carried into the common window are excluded; this is a filtered comparison, not a fresh equity restart.

AUDJPY M30 long's reported +ZAR 16,586.68 is based on just 17 closed trades and a position still open from 19 February. There are no new closed trades inside the recent common window. NAS100 M15/M30 also contain positions open since May/April. Their apparent results do not establish ongoing opportunity frequency. USDZAR has only 4–7 trades. I did **not** install “optimized” auto profiles for these three instruments. Use Custom for deliberate experiments.

### The 90-minute hypothesis

Export times are SAST (UTC+2), confirmed by you. They were converted to each run's explicitly configured session timezone before calculating entry delay. The London settings were **09:00–17:00 Africa/Johannesburg**, not the conventional 08:00 London-local window. The Asian settings were 00:00–08:00 Europe/London; New York 08:00–17:00 America/New_York. Changing the chart timezone does not change these Pine inputs.

In XAUUSD M15 short/retest, the 8 entries before 90 minutes had budget-normalized PF 0.62; the 25 later entries had 2.28. That supports testing a delay. But GBPJPY M5 both/retest shows the reverse: PF 5.93 before 90 minutes (11 trades), 0.50 later (13). **Do not impose 90 minutes universally.** These are selected subsets of trades the old system already took; a real delay changes the setup path and can create different entries. A new backtest is required.

The new gold auto profile uses M15, NY, short, and a **90-minute hypothesis**; the three major/cross-pair profiles use M5 London and no added delay. Auto profiles are explicitly research candidates. Their old entry models are not falsely labeled as equivalent to the new breakout/retest/continuation rules.

## Paper trading: encouraging, but not validation

The six CSVs contain 10 consolidated closed trades (5 wins, 5 losses), with 13 realized balance events because some trades were closed in parts. Net PnL is ZAR 4,890.11 and the balance moves from ZAR 10,000 to ZAR 14,890.11. Trade PnL reconciles to the balance ledger within ZAR 0.001. PF is 3.10; removing the single best trade leaves +ZAR 1,563.50. The first XAUUSD loss alone was ZAR 1,576.30, or 15.76% of the starting balance.

The 50% win rate has an approximate Wilson 95% interval of **23.7%–76.3%**, even before accounting for trade dependence or selection. Ten trades cannot establish a stable edge. The exports lack original setup annotations, chart timeframe and reliable planned SL/risk for every trade, so I cannot attribute success specifically to order blocks, FVGs, Fibonacci or the delay.

The paper order history shows **50x**, not 500x, leverage on populated rows and 11 rejected orders. Check the paper account separately from Strategy Properties. Two order rows were present in the exported order snapshot; the positions CSV was empty. These are export-time observations, not a live account check. No orders or account settings were changed.

## Limitations in v1 and what changed

1. **Session/range anchoring.** V1 started the ORB on the first available session bar. A chart starting mid-session could form a shifted range. V3 anchors to the configured scheduled opening time, requires complete contiguous coverage, and refuses incomplete/unaligned ranges.
2. **Lifecycle leakage.** V1's full-framework retest and continuation checks did not consistently respect invalidation/session state. A failed early direction could also lock out later setups. V3 requires separate confirmed breakout, retest and continuation bars; invalidation happens first, has a timeout, and requires a fresh break before retrying.
3. **Context was not modeled.** V1 was mainly an ORB execution approximation. V3 adds explicitly defined, confirmed-bar OB/FVG/Fib context, with selectable requirements. These filters may reduce frequency without improving expectancy; test them incrementally.
4. **Estimated versus executed prices.** V1 sized and anchored its absolute bracket at the signal close, although market entries filled later. V2 uses loss/profit tick distances relative to the actual simulated fill. Target/stop prices may therefore shift away from the originally estimated structural anchor after a gap. This preserves the modeled distance ratio, not exact structural placement or exact net 3R.
5. **Session exits changed the payoff.** V1 often closed early, and its first available outside-session bar could be much later than the scheduled end. V2 has no session-end flatten. Manual plans remain active until a level is touched, as requested. Positions held overnight incur risks and possible financing that this model does not automatically price.
6. **Exit-variable clearing.** In v1, a new entry submitted on a bar where an earlier position had just closed could have its new `activeStop`/`activeTarget` variables cleared by the end-of-bar reset. This is a code-path risk, not a proven explanation for every long-held export trade. V2 submits the bracket with the entry and does not run that reset.
7. **Excessive risk/cost sensitivity.** Default sizing is now 1% risk, with a margin reserve and optional cost allowance for sizing. Broker spread, commissions, swaps, contract size and margin rules still need your inputs. No news filter or broker integration is claimed.
8. **One selected session only.** V3 can scan all three configured windows, with at most one qualified signal per session start date. That is a ceiling, not a daily quota to force. Overlapping manual plans are possible; the tester intentionally cannot hedge them simultaneously.

## Test plan and decision rules

Your 25% break-even calculation is right for fixed +3R winners and −1R losers before costs: `p × 3 − (1−p) = 0`. With average cost `c` measured in R, the threshold becomes `(1+c)/4`. Early exits and variable losses require using the actual average win/loss instead. A 45–55% win rate at 3R would imply a very strong +0.8R to +1.2R pre-cost expectancy; it is an aspiration, not an outcome code can guarantee.

1. **Baseline audit:** rerun v1 and v2 with identical feed, date range, chart interval, session definitions, 1% risk and realistic costs. Keep original 2.75R/session-exit settings only in the labeled v1 control. Do not mix these with 3R hold-to-exit results.
2. **Minimal ablation:** on the shortlisted pairs compare v2 ORB baseline, baseline plus a 90-minute delay, baseline plus one context requirement, then the two-context default. Keep direction, stop, target, feed and costs fixed within each comparison. Also test both directions to detect whether the short/long-only selection was overfit.
3. **Separate timing experiments:** ORB offset 0/duration 30 with entry delay 90 is different from ORB offset 90/duration 30 (earliest entry after minute 120). Test them as separate variants. Do not mix London-local and fixed-SAST timing in the same experiment.
4. **Historical robustness:** use common dates across pairs and enough history for multiple regimes. Freeze the shortlisted parameters before checking an untouched later period. The 70/30 chronological summaries in `analysis_evidence.json` are retrospective stability diagnostics, **not genuine out-of-sample validation**, because these exports have already been inspected.
5. **One-week forward usability test:** freeze a version/settings screenshot and record every qualified signal, including skipped trades and no-signal sessions. Use paper/manual decisions only. Review after a week for timing, invalidations, sizing and clarity. A quiet week is useful usability evidence, not proof of no edge; a profitable week is not proof of robustness.
6. **Evaluation:** prioritize net expectancy, PF, drawdown, loss streaks, sample count and consistency across subperiods, not the highest win rate. Aim to collect at least 100–200 closed, consistently defined signals over time; even that is not a guarantee or immunity from regime change. Track spread/cost sensitivity and concentration in the best few trades.

Upload the full Strategy Tester XLSX for each run, not just its summary screenshot. Include feed, interval, profile, direction, session timezone/window, ORB offset/duration, delay, context mode, stop, target, dates, commissions, slippage and Bar Magnifier setting in the filename or a settings screenshot. For manual trades include signal time in SAST, screenshot at signal, actual entry/exit, original SL/TP, quantity, costs, whether you followed/skipped it, and the reason. Mark candles that touched both SL and TP as ambiguous unless lower-timeframe evidence resolves the sequence.

## Reproduce the analysis

Run `tools/analyze_orb_results.py` with Python 3 and openpyxl. It reads the originals without modifying them and regenerates `analysis_evidence.json` and `run_comparison.csv`. JSON includes source hashes, properties, reconciliation checks, open positions, duplicates, closed trades, timing subsets and common-window summaries. The companion notebook invokes the same pipeline. Do not add paper trades together with simulated trades or add repeated runs as though they were one portfolio.

## New-engine smoke checks — not performance validation

In the signed-in TradingView session on 14 September, backtest v2 compiled and executed with ZAR 10,000, 500x long/short leverage, 1% risk, 3R, zero commission, one tick slippage, bar-close calculations and next-tick order execution. Standard hollow-candle charts were used. Current account history limits were shorter than some of the supplied exports. The first checks below used the **whole-setup delay** implementation; the final tool separates signal-only delay (default) from the optional whole-setup delay. They are not interchangeable results.

- **FX:GBPJPY M5, default short/London/two-context:** the available 16 August–14 September window produced one closed short, entered 24 August 14:20 SAST and stopped at 15:20. PnL was −ZAR 100.29. This checks order sizing and exit execution, not an edge.
- **FX:XAUUSD M15, short/NY/90-minute wait/two-context:** the available 1 June–14 September window produced no trades.
- **Same gold test with only the minimum context count changed from two to one:** four closed shorts, all stop losses (−ZAR 71.39, −98.85, −59.37 and −91.10; total −ZAR 320.71). Fractional quantity rounding can put realized risk below the nominal budget. This was a labeled sensitivity check; the delivered two-context default was not changed to chase signal count.

### Final delivered default: signal-only delay

Both exact final source files were subsequently checked against the editor text and successfully compiled in place. With **FX:XAUUSD M15, 1 June–14 September 2026**, Auto profile, NY short, 90-minute signal delay, `Delay breakout search too = Off`, and the default **two context matches**, the final strategy produced **6 closed trades: 2 wins and 4 losses**. TradingView reported **+ZAR 136.02 (+1.36%)**, profit factor **1.405**, and maximum drawdown **ZAR 250.92 (2.42%)**. Gross profit was ZAR 471.68 and gross loss ZAR 335.66. The risk/target/cost assumptions remained 1%/3R/zero commission/one tick slippage.

This 33.33% win rate is a tiny, in-sample smoke-test result, not proof of the requested 45–55% target or an independently validated edge. The different outcome from the earlier whole-setup-delay check demonstrates that delaying only the signal and delaying the breakout search are materially different rules. Keep the switch fixed when comparing runs.

### Gold longs and both directions

At your request, I then changed **only Allowed direction** and reran the final engine on the same FX:XAUUSD M15 / NY / 1 June–14 September window, with the same 90-minute signal delay, two context matches, 1% risk and 3R target:

| Allowed direction | Closed trades | Wins / losses | Win rate | Net PnL (ZAR) | PF | Max drawdown |
|---|---:|---:|---:|---:|---:|---:|
| Short only (Auto profile) | 6 | 2 / 4 | 33.33% | +136.02 | 1.405 | 2.42% |
| Long only | 2 | 0 / 2 | 0.00% | −147.78 | 0 | 1.48% |
| Both | 8 | 2 / 6 | 25.00% | +38.59 | 1.089 | 3.35% |

The two longs entered 26 June 15:45 SAST and 9 July 17:00 SAST; both stopped (−ZAR 71.06 and −ZAR 76.72). No open trade was listed in either direction-comparison run. Both-mode gross profit was ZAR 471.68, gross loss ZAR 433.09 and maximum drawdown ZAR 348.34. These are UI-observed results, not new exported workbooks.

Both-mode PnL is not the arithmetic sum of the separate runs: equity-dependent sizing and quantity rounding change subsequent sizes. In this test the 27 July short was quantity 0.1 / −ZAR 50.35 in Both mode, versus quantity 0.2 / −ZAR 100.70 in Short-only mode. More generally, the one-position limit and one-signal-per-session rule can also change which trades occur.

**Two longs are not enough to reject buying gold.** The old exports contain no standalone gold long-only run. Their M15 both-direction retest PF was 0.82 (60 trades), versus short-only PF 1.44 (33), which explains the initial short research profile but does not validate a permanent directional restriction. The 90-minute timing hypothesis was derived from short trades, so test long-only at 0 versus 90 minutes as a separate, fixed-parameter experiment. Also retain Both as a control to see whether direction selection was overfit. Neither these samples nor the new filters establish a reliable edge. No default direction was silently changed on the basis of two losses.

### Are our rules excluding the opening move?

You confirmed that “market open” means the configured **08:00 New York** start, not 09:30. I ran a two-by-two diagnostic on the same final source, dates, feed, M15 interval, 30-minute ORB, Both directions, 1% risk and 3R target. Only the explicit signal delay and context requirement changed; the breakout/retest/continuation sequence and all other filters remained in place. `Delay breakout search too` stayed Off.

| Minimum signal delay from 08:00 | Context requirement | Closed trades | Win rate | Net PnL (ZAR) | PF | Max drawdown |
|---|---|---:|---:|---:|---:|---:|
| 90 min | Two matches | 8 | 25.00% | +38.59 | 1.089 | 3.35% |
| 0 min | Two matches | 8 | 25.00% | +38.59 | 1.089 | 3.35% |
| 90 min | None: ORB baseline | 20 | 25.00% | +118.22 | 1.109 | 7.79% |
| 0 min | None: ORB baseline | 20 | 25.00% | +92.67 | 1.084 | 8.04% |

These are Strategy Report UI observations, not new XLSX exports. Baseline 90-minute gross profit/loss were ZAR 1,198.32 / 1,080.09 and maximum drawdown ZAR 828.72. Baseline zero-delay gross profit/loss were ZAR 1,198.32 / 1,105.65 and maximum drawdown ZAR 854.27. Rounded components may differ from displayed net profit by one cent. All runs still use placeholder costs; these tiny positive totals are not evidence of a robust tradable margin.

**The important constraint is structural timing.** A 30-minute ORB ends at 08:30. On M15, the earliest separate confirmed breakout, retest and continuation can close at 08:45, 09:00 and **09:15** respectively. Thus `delay = 0` still cannot signal during the first **75 minutes** from 08:00, assuming perfectly aligned bars and an otherwise valid setup. A 90-minute signal delay only moves that earliest boundary another 15 minutes, to 09:30. This explains why removing the extra wait need not produce many additional opportunities. It does not prove every missed opening move would have been profitable.

The context gate clearly reduces accepted trade frequency in this window (20 baseline versus 8 filtered), but its removal did **not** improve win rate, and drawdown was substantially higher. This is a whole-run counterfactual comparison, not simply a claim that 12 identical discarded trades were added: state transitions, session quotas, open positions and equity-dependent sizing can change the path.

Other deliberately restrictive rules remain: displaced breakout, ORB-edge retest, two context touches on the same retest candle when enabled, continuation beyond both prior extremes, stop-distance bounds, expiry, and one signal per session. A trend that breaks once and never revisits the ORB edge is intentionally missed. The three-stage entry also gives up part of the initial move before estimating a 3R target beyond the opposite-ORB stop.

**Next diagnostic, not an automatic fix:** first compare M5 versus M15 with the same 30-minute ORB and zero extra delay, turning off the profile-timeframe lock for that experiment. M5 reduces the theoretical earliest confirmation to 08:45 without changing the sequence. Separately, a close-breakout or retest-close entry mode would be needed to test earlier entry mechanics; the current `ORB baseline` does not disable retest/continuation. A 5- or 15-minute ORB is another separate experiment, not the same setup. Do not simultaneously shorten the ORB, remove context and change stops—then we would not know which change helped. No new entry-model code was introduced during this diagnostic.

The manual indicator's temporary one-context/30-day display settings were restored to the delivered two-context/five-day defaults. Its signal labels and SL/TP lines were visually inspected during the earlier sensitivity check; the final chart shows the manual indicator, with the simulated-order overlay hidden. No alerts or broker orders were activated. See `VALIDATION.md` for source identities and the scope of verification.

Strict filtering may leave a week with no qualifying gold signals. Use the baseline and filter-ablation plan above to find out which conditions help; do not mistake a working script or more conditions for better returns. Historical alert delivery, live broker fills, long-horizon robustness and broker-specific costs were not validated by these smoke checks.

TradingView displayed a saved-script plan limit when saving to its library. No subscription was changed and no older saved script was overwritten. The standalone local Pine files are the authoritative deliverables.

## Platform references

[TradingView time and timezone behavior](https://www.tradingview.com/pine-script-docs/concepts/time/) explains why chart display time and script session time differ. [TradingView strategy execution](https://www.tradingview.com/pine-script-docs/concepts/strategies/) documents the broker emulator and fill assumptions. [Export strategy data](https://www.tradingview.com/support/solutions/43000613680-how-to-export-strategy-data/) describes downloading the report. [Alert behavior](https://www.tradingview.com/pine-script-docs/concepts/alerts/) covers real-time alert creation; historical markers do not imply historical notifications were delivered.
