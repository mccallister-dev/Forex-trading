# ORB manual v3 and backtest v2 — setup

## 23 September 2026 — manual indicator display update

These changes apply only to `ORB_ICT_Manual_Signals_v3.pine`. The separate Strategy Tester script was not regenerated or changed.

- The dashboard is reduced to status, **Signal Flow**, the three session states and manual-plan count. Profile/direction, ORB timing, risk/target, sizing and entry/context rows were removed from the panel; their inputs still control the indicator.
- **Signal Flow** shows the latest qualified signal from the current SAST trading day on M5, M15 and M30. A dash means that timeframe has not produced a qualified signal today. It does not turn a higher-timeframe signal into a signal on the chart timeframe.
- Asian, London and New York ORB colours, line width and transparency are configurable under the display inputs. BUY and SELL marker colours are configurable too.
- **Maximum ORB retest depth (%)** replaces the ATR retest tolerance. It measures the permitted penetration back inside the broken ORB as a percentage of that ORB's own width: 0% permits a boundary touch only; 25% permits the nearest quarter; 100% permits the full range. The qualifying candle must still reclaim and close outside the broken edge.

Changing this percentage changes the signal engine, so do not compare results against older settings without recording the value.

Updated 15 September 2026: restored independent entry choices. Existing 14 September research results refer to the earlier engine, not newly tested close-breakout results. Backups: `Backups/2026-09-15-before-entry-options`.

Use `ORB_ICT_Manual_Signals_v3.pine` for discretionary chart signals and alerts. It is an **indicator**, places no orders and has no broker connection. Use the separate `ORB_ICT_Backtest_Strategy_v2.pine` for TradingView Strategy Tester simulations. Both are standalone Pine v6 scripts. Since the 23 September manual-only update, their signal engines are no longer identical: the backtest retains its earlier ATR retest rule until a separate backtest change is requested.

Read `ORB Research 2026-09-14/README.md` for the actual export findings, limitations and one-week test plan. These new rules are research hypotheses, not a promised win rate.

## Install and start

1. Open TradingView with your intended broker feed and standard OHLC candles (regular or hollow candles are suitable; no Heikin Ashi, Renko, range or other synthetic-price chart).
2. Open Pine Editor, create a **new** script and paste the entire matching `.pine` file. Do not paste Markdown fences. Keep the old scripts as controls.
3. Add to chart. Open the script's Settings and check the status panel for blocked configuration messages. TradingView cannot have a script automatically change your chart interval.
4. For the auto research candidates, set **XAUUSD to 15 minutes**, and **EURUSD, GBPJPY or GBPUSD to 5 minutes**. Other symbols use your Custom/fallback inputs. To compare another timeframe, disable `Require profile chart timeframe`; it still must be time-based, at least 1 minute, no longer than the ORB, and divide the ORB duration with aligned bars. For an H1 chart, for example, use at least a 60-minute aligned ORB and a higher trend timeframe if that filter is on.
5. The default scans only the profile's session. Choose `All enabled sessions` to scan Asian, London and New York. The same interval, direction, ORB offset/duration and delay apply to all enabled sessions on that chart. Use separate instances/settings if you need different rules per session. There is at most one **qualified** signal per session start date, not a forced signal every session.

### Auto candidates

| Pair | Chart | Session | Direction | Minimum signal delay after open |
|---|---|---|---|---:|
| XAUUSD | M15 | New York | Short | 90 min — hypothesis |
| EURUSD | M5 | London | Long | 0 min beyond ORB completion |
| GBPJPY | M5 | London | Short | 0 min beyond ORB completion |
| GBPUSD | M5 | London | Both | 0 min beyond ORB completion |

All use a 30-minute ORB by default. Inputs can override direction/delay/session; set `Profile = Custom` for full control. The profile does not choose the entry trigger: use `Entry model` independently. Continuation remains the default for continuity, not because it is proven best. Restored modes retain the new engine's guards and do not exactly reproduce v1 results. No automatic “best” setting is asserted for AUDJPY, USDZAR or NAS100.

**To test gold longs or both sides:** leave the Auto profile selected, then change **Inputs → Allowed direction → Long only** or **Both**. This overrides the short-only research profile without changing its M15 chart requirement, New York session or 90-minute delay. Make the same change separately in the manual indicator and tester when comparing them. `Both` means either qualified direction, not simultaneous hedged positions, and still permits only one qualified signal per session. The report includes an identical-settings comparison of all three directions; its two long trades are far too few to rule out longs. Test delay 0 versus 90 separately for buys because the original timing hypothesis came from shorts.

## Exactly what creates a signal

1. A complete range is collected from the configured session open plus ORB offset. Missing, partial or unaligned coverage is rejected rather than silently shifting the range.
2. After the range ends, a fresh confirmed close crosses beyond an ORB edge with a directional displacement candle. Default displacement: body at least 0.6 ATR and at least half the candle's range. The same breakout rule applies to all entry modes.
3. `Entry model` independently selects **Close breakout** (signal on that breakout close), **Break + retest** (signal on a later qualifying ORB-edge retest/rejection close), or **Break + retest + continuation** (another later close beyond both breakout and retest extremes). Retest depth is the configurable percentage of ORB width described above. No mode implicitly upgrades into another mode.
4. `Context filter = Off` removes the OB/FVG/Fib gate without changing entry timing. `Required` applies the selected minimum count. Close breakout checks existing OB/FVG touches on its breakout candle. Both retest modes check OB/FVG/Fib together on the qualifying retest candle. The optional confirmed HTF trend and stop-distance guards remain independent and apply to every signal.
5. All signals must occur at/after the minimum delay and before the last-entry cutoff. **Close breakout does not queue early breakouts:** a pre-delay or context-rejected breakout requires a new crossing to qualify later. **Break + retest** may build a setup before the wait, but must have a qualifying retest at/after the delay; an early retest is not queued for entry on an arbitrary later candle. Continuation can store an earlier qualified retest and wait for a valid later continuation. `Delay breakout search too` additionally prevents setup formation before the delay, based on the breakout bar's opening time.
6. A signal appears only at the selected confirmation candle's close. The session's signal allowance is consumed. Failed or expired setups can start again on a fresh break, but not confirm from an invalid state. The tester still fills on the next tick, not necessarily at the signal close.

There is no literal “ORB equals 50% win probability” calculation. ORB is a mandatory structural gate; context is an optional separate gate. A context count is evidence count, not probability, recommendation or confidence.

### Objective context definitions

- **Order block:** the most recent opposing candle (full high/low range) found within the search limit before a displaced close beyond the preceding structure lookback. The zone becomes available only once that structural break is confirmed.
- **FVG:** a confirmed three-candle price gap (`low > high[2]` for bullish, reverse for bearish), with minimum ATR width and a displaced middle candle.
- **Fib:** retracement band, default 50%–78.6%, measured from the opposite ORB edge to the breakout candle's extreme. This is a deliberate, fixed impulse approximation, not a discretionary swing-selection algorithm. Anchors freeze at the breakout and do not move to future extremes.

Fib is **not counted for Close breakout**: a later retracement of the newly formed impulse does not exist yet, and counting the breakout candle against its own newly created Fib band would manufacture evidence. Existing OB/FVG zones are available; enabling only Fib, or requiring three matches for Close breakout, blocks signals and displays an explanation. With Context Off this restriction does not block the entry. For retest modes, Fib behavior is unchanged.

Only the latest bullish/bearish OB and FVG are retained. Zones expire after the configured number of chart bars or a close through their far edge. They may survive a partial touch; there is no “first touch only” claim. A zone formed on the retest candle cannot count on that same candle. These approximations may differ from how you draw ICT concepts manually. The signal caption identifies the matched context; it does not draw a large historical zone overlay.

Migration: the previous `ORB + context` selection maps to **Break + retest + continuation / Context Required**; previous `ORB baseline` maps to **Break + retest + continuation / Context Off**. Verify both controls after updating rather than relying on TradingView to migrate the removed dropdown values. `Minimum context matches = 1` plus a single enabled applicable context lets you test one filter at a time. Impossible counts block signals. The optional trend filter uses the last completed HTF close and EMA; that timeframe must exceed the chart interval.

For a plain close-breakout control: choose **Close breakout**, **Context Off**, **Entry delay Custom / 0**. Keep direction, ORB, stop, target, risk and costs fixed when comparing entry modes. These choices do not remove the displacement or complete-range guards. Entry mode now appears on the panel, manual captions, detailed alert messages and tester entry comments.

## Custom ORB versus delayed entry

- **First 30-minute ORB, wait 90 minutes:** offset 0, duration 30, entry delay mode Custom, delay 90.
- **Build an ORB starting 90 minutes after open:** offset 90, duration 30. It finishes at minute 120; the selected entry sequence starts after that range ends.
- Align offset, duration and actual window endpoints to the chart's bar boundaries. The complete ORB must finish before the last-entry cutoff.

**Zero delay is not an opening-tick entry.** With an 08:00 session and a 30-minute ORB, the theoretical earliest signal times are:

| Entry model | M5 chart | M15 chart |
|---|---|---|
| Close breakout | 08:35 | 08:45 |
| Break + retest | 08:40 | 09:00 |
| Break + retest + continuation | 08:45 | 09:15 |

Times are New York local time for the NY window. These are lower bounds with aligned bars and zero extra delay, not promised signals. Context, delay and other guards may defer or prevent a signal. Set the chart interval yourself and disable `Require profile chart timeframe` when testing M5 gold with its Auto profile.

Defaults preserve your exports' clock definitions: Asian 00:00–08:00 Europe/London; London 09:00–17:00 Africa/Johannesburg; New York 08:00–17:00 America/New_York. The Asian window is a configurable FX convention, not a universal market opening bell. To test the London-local 08:00 open, change both the window and timezone; that is a different experiment. IANA timezones adjust for DST. Signal alert timestamps are explicitly SAST. Use a single continuous session window; the weekday toggle controls the session **start** day, including overnight windows.

## ZAR 10,000 and 1:500 leverage

In **Strategy Settings → Properties**:

| Setting | Value |
|---|---|
| Initial capital | 10,000 |
| Base/account currency | ZAR |
| Margin long and short, if shown as percentages | 0.2% each |
| Long and short leverage, if shown as multiples | 500x each |
| Pyramiding | 0 |
| Recalculate after fills / every tick | Off |
| Fill orders on bar close | Off |
| Commission and slippage | Set to your actual broker/feed assumptions |

The conversion is `margin % = 100 / leverage`: **100/500 = 0.2%**, not 20% and not 0.002%. The script's `Exposure ceiling` should match the Properties leverage. [TradingView strategy documentation](https://www.tradingview.com/pine-script-docs/concepts/strategies/) explains simulated fills and margin behavior.

In **Inputs**, default risk is **1%** and target is **3R**. On a ZAR 10,000 account, 1% is a **ZAR 100 planned risk budget**, not an instruction to put the entire account on margin. Leverage changes collateral requirements; it does not make a given stop loss smaller. Ten consecutive exact 10% losses leave about 34.9% of equity, whereas ten 1% losses leave about 90.4%, before costs/gaps.

Sizing formula:

`risk quantity = (equity × risk %) / [(stop distance + cost allowance) × symbol point value × quote-to-ZAR rate]`

`exposure quantity cap = equity × leverage × allowed margin allocation / (entry price × point value × quote-to-ZAR rate)`

The smaller quantity is rounded **down** to the quantity step. The default maximum margin allocation is 25% of equity, leaving a reserve; this is independent of the 1% risk budget. Daily currency conversion is an estimate, not your broker's exact intraday conversion. Missing conversion prevents tester orders and shows unavailable manual sizing. In the indicator, update `Manual account equity (ZAR)` yourself; in the strategy, equity comes from Strategy Tester. The Properties default order size is not used because the script passes explicit quantities.

Verify quantity units on the exact feed. XAUUSD quantities may represent ounces/contracts rather than lots; a broker's 0.01-lot order might correspond to a quantity of 1 when a full lot is 100 ounces, **but do not assume this for every feed**. Forex units and CFD point values also vary. Set `Broker quantity step` in TradingView quantity units, and `TradingView quantity per broker lot` only after verification. Zero leaves broker lots hidden.

The sizing cost allowance only reduces the chosen size. It does **not** deduct spread/fees from reported performance. Set actual commission and slippage separately; the supplied 0% commission and one tick slippage are placeholders. Fixed slippage cannot fully reproduce variable spread, news spikes, swaps or broker stop-out rules. Your exported paper order history used 50x on populated rows: the paper account's leverage is a separate setting from Strategy Tester. Neither script changes a real or paper broker account.

## Stops, targets and overlapping plans

Manual labels show the **signal-close estimate** of entry, SL and TP. The default stop is beyond the opposite ORB edge with a 0.1 ATR buffer (at least one tick). `Pullback extreme` is an optional alternate stop: it uses the qualifying retest candle in retest modes, or the breakout candle extreme for Close breakout because no pullback exists. Levels freeze when the signal is issued and remain active across session/day boundaries until a later bar touches SL or TP. No same-signal-candle exit is counted. If a later candle touches both, the plan is marked **ambiguous**, not arbitrarily a winner.

A touched level is not proof of a real fill or realized profit. You choose whether to trade and must recalculate from your actual entry, spread and quantity. The indicator does not track your real account, move stops, automate break-even or execute trades. Closed-plan drawings are kept for five observed SAST chart days by default; still-active plans are not expired. A resource ceiling of 140 drawn plans suppresses further drawings (not signal markers/alerts), explicitly counted in the panel. It does not silently delete existing active plans.

The strategy uses the **same qualified signals**, but its market order fills on the next available tick/bar open. Brackets are relative tick distances from that modeled fill, so the plotted actual tester SL/TP can differ from the manual signal-close estimates after gaps/slippage. Entry-to-bracket price distances target the chosen R; net realized R can still differ due to exit slippage, fees, currency conversion or margin liquidation. Stops are not guaranteed fills.

The tester allows only one net position and no reversals. If a position is open, the signal is skipped and counted; same-bar session conflicts use Asian → London → NY priority. A skipped signal still consumes that session's **signal** quota. Manual plans can overlap, including opposite directions; their level-touch history is therefore not identical to the strategy's trade list. There is no forced session/end-date exit in either tool. The end date limits new signals only; open trades/plans continue toward SL/TP.

The 1% budget is **per plan**, not an account-wide exposure controller. Multiple charts and overlapping plans can accumulate much greater risk, especially on correlated USD pairs. Set a separate total open-risk limit for your manual account and record which signals you skip because that limit is reached. The indicator cannot see positions taken on other charts or at your broker.

## Alerts and exports

On the **manual indicator**, create an alert with condition `ORB Manual v3 → Any alert() function call` for the full symbol/session/SAST time/estimated entry/SL/TP/quantity/context message. Calls occur only on confirmed bars; multiple sessions can each emit a message on one bar. Alternatively use `Qualified BUY` or `Qualified SELL` and choose once-per-bar-close. Alerts are not broker instructions. Recreate alerts after changing code, symbol, interval or settings because TradingView alerts use saved snapshots. No alerts were activated on your behalf.

For backtests, open **Strategy Tester / Strategy Report**, select the new v2 strategy, run the fixed comparison settings, and use **Download/Export**. Upload the complete XLSX (or all report tabs if your UI exports CSV separately), including Trades and Properties. TradingView features and export limits depend on the account plan; [official export instructions](https://www.tradingview.com/support/solutions/43000613680-how-to-export-strategy-data/) show the workflow.

Suggested filename: `FX_XAUUSD_M15_NY_short_ORB0-30_delay90_context2_3R_risk1_dates.xlsx`. Add a settings screenshot and broker cost assumptions. Keep date ranges/feed/model consistent across comparisons. Where your plan allows it, compare Bar Magnifier on/off and inspect trades with both bracket levels inside one chart candle. Do not combine overlapping runs as if they were independent portfolio returns.

## Maintenance

Edit `tools/orb_v3_manual_core.pine.inc` for the manual indicator's signal/display engine and `tools/orb_v3_manual.pine.inc` for its plan rendering. The Strategy Tester continues to use `tools/orb_v3_core.pine.inc` plus `tools/orb_v2_strategy.pine.inc`. Run `python3 tools/build_orb_v3.py --target manual` after manual-only edits; `--check --target manual` detects generated-source drift without touching the strategy. Recompile the exact generated file in TradingView after a change. A successful compile/smoke test proves execution, not profitable out-of-sample performance.
