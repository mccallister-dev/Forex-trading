# Delivery audit — 14 September 2026

## Source identity and execution

The two standalone Pine v6 files were generated from the same signal engine. The exact final file contents were compared with TradingView editor text (normalizing only CRLF/LF line endings), then **Update on chart** successfully compiled each attached script in the signed-in session. No compile success is inferred from Python tests.

| Artifact | SHA256 |
|---|---|
| `ORB_ICT_Manual_Signals_v3.pine` | `699db050c2b526940ca2f16e137a65f2e2401163d940aa7d22f9282d33b51baa` |
| `ORB_ICT_Backtest_Strategy_v2.pine` | `6d209b491c1519840ae6f7e46a99bc8e9a8f8d936648dbaffc43a50ae3c0e87a` |
| Common signal engine embedded in both | `abd52057555c54969b118b570c7ecf2f2aa628e771db163476fc2cdc82104c85` |

`tools/build_orb_v3.py --check` verifies generated-source parity. Nineteen supplementary tests passed, including source guards, sizing arithmetic, trade-grain handling, reconciliation, duplicate recognition and preservation of the original Pine sources. The five-cell companion notebook was executed top-to-bottom successfully against the final sources. These checks do not emulate the Pine runtime or prove every possible price path.

## Final default-mode TradingView smoke test

- Symbol/feed: **FX:XAUUSD**, standard hollow OHLC candles, **M15**.
- Available report window: **1 June–14 September 2026**; timestamps displayed as **UTC+2**.
- Auto research profile: NY short, ORB offset 0/duration 30 minutes, signal delay 90 minutes, **breakout-search delay Off**, minimum context matches **2**.
- Initial equity **ZAR 10,000**, risk **1%**, target **3R**, long/short leverage **500x**, pyramiding 0, commission 0%, slippage 1 tick. Costs are placeholders.
- Bar-close calculation, next-tick execution, default bar-detail assumptions. No fill recalculation, tick recalculation or forced session flatten.
- **6 closed trades**, **2 TP / 4 SL**, **33.33%** win rate.
- **+ZAR 136.02 / +1.36%**, PF **1.405**, maximum drawdown **ZAR 250.92 / 2.42%**.
- Gross profit **ZAR 471.68**; gross loss **ZAR 335.66**.

| Entry (SAST) | Exit (SAST) | Outcome | PnL (ZAR) |
|---|---|---|---:|
| 2 Jun 15:30 | 3 Jun 15:30 | TP | +234.95 |
| 3 Jun 17:45 | 4 Jun 03:00 | SL | −84.75 |
| 9 Jun 16:15 | 9 Jun 18:30 | TP | +236.73 |
| 21 Jul 15:45 | 21 Jul 16:15 | SL | −98.90 |
| 27 Jul 16:30 | 29 Jul 20:45 | SL | −100.70 |
| 3 Aug 15:30 | 4 Aug 02:00 | SL | −51.31 |

Source: TradingView report and trade-list UI observed during this validation. This is a transcription, not a newly exported workbook. Earlier whole-setup-delay checks are separately labeled in `README.md`; they must not be conflated with these final defaults.

## Direction-only comparison requested during handoff

On the same final source/feed/timeframe/date range and unchanged inputs except Allowed direction:

| Direction | Closed / winners | Net PnL (ZAR) | PF | Maximum drawdown |
|---|---:|---:|---:|---:|
| Long only | 2 / 0 | −147.78 | 0 | ZAR 147.78 / 1.48% |
| Both | 8 / 2 | +38.59 | 1.089 | ZAR 348.34 / 3.35% |

Both long entries were observed in the trade list: 26 June 15:45 → 29 June 07:30 SAST (SL, −ZAR 71.06) and 9 July 17:00 → 10 July 10:00 (SL, −ZAR 76.72). No open trade was shown. Both-mode gross profit/loss were ZAR 471.68 / 433.09. The different equity path rounded the 27 July short down to quantity 0.1 rather than 0.2, so separate-run PnLs cannot simply be added. The strategy's BUY order path therefore also executed successfully; this does not independently validate the manual BUY label rendering or establish the quality of long signals.

## Opening-time / rule diagnostic

The user confirmed 08:00 New York as the session open. Keeping Both directions and all other test assumptions fixed, the final engine was run with zero extra signal delay / two context matches (8 trades, 2 winners, +ZAR 38.59, PF 1.089, 3.35% max drawdown), zero delay / ORB baseline (20 trades, 5 winners, +ZAR 92.67, PF 1.084, 8.04% max drawdown), and 90-minute delay / ORB baseline (20 trades, 5 winners, +ZAR 118.22, PF 1.109, 7.79% max drawdown). Results and limitations are tabulated in `README.md`. These are controlled UI-run comparisons, not holdout validation or exported workbooks.

Source inspection confirmed that the three separate post-ORB confirmation bars imply a theoretical earliest 09:15 signal on M15 with a 30-minute ORB starting 08:00, even with the delay input at zero. This is a mechanical lower bound, not an observed guarantee of an entry. No faster-entry implementation was added during the diagnostic.

## Requested behavior and verification scope

| Requirement | Delivered behavior / check |
|---|---|
| Separate tester strategy and manual tool | Separate `strategy()` and `indicator()` artifacts; manual file contains no strategy order calls or broker connection. Both compiled. |
| Pair/timeframe/session/delay choices | Exploratory auto profiles plus Custom overrides; actual chart interval must be selected by the user. Gold and GBPJPY were used for execution smoke checks, not all feeds. |
| Custom ORB | Scheduled session anchor plus offset/duration; source guards reject incomplete or unaligned ranges. |
| Confirmed signals with context | Shared breakout → later retest → later continuation engine with defined OB/FVG/Fib gates. No future-confirmed pivot data is used. |
| Buy/sell labels and estimated SL/TP | Rendered manual short labels, quantity/context captions and horizontal SL/TP lines were visually inspected in the labeled one-context sensitivity check. The symmetric buy branch was source-reviewed, not independently exercised in a final live-chart scenario. |
| Plans persist to SL/TP | Source preserves active plans across session/day changes and starts touch checks after the signal bar. Same-bar SL+TP is marked ambiguous; that branch was source-checked rather than visually triggered. |
| Up to one signal per session | Independent session-start-date quotas; three-session scan option. No forced daily quota. Overlapping manual plans differ from the tester's one-net-position constraint. |
| Alerts | Confirmed-bar detailed alert calls and static BUY/SELL conditions supplied. Alerts were not activated; live notification delivery is untested. |
| Risk and leverage | ZAR 10,000 and 500x confirmed in Strategy Properties; 1% sizing checked arithmetically and in actual simulated trades. Broker quantity conventions, fees and account-wide exposure still require user verification. |
| Usable handoff | Guide, findings, settings, export workflow, reproducible audit notebook and one-week test protocol supplied. Final manual inputs restored to context count 2 and five-day completed-drawing retention; strategy overlay hidden to leave the manual chart clear. |

## Safety and remaining limits

Original Pine files and input exports remain unchanged; dated backups are in `Backups/2026-09-14-before-manual-v3`. No live or paper orders, account leverage changes, subscriptions, or alerts were submitted. TradingView's saved-script library limit prevented adding a new saved library item; no existing saved script was overwritten. Keep the standalone local files as the authoritative copies.

The deliverables are ready for controlled backtesting and a forward usability test, **not validated for live profitability**. The requested 45–55% win rate at 3R has not been established. Real spread/fees/swaps, gaps, news conditions, broker fills, overlapping account risk, multiple market regimes and unseen holdout data still need testing. The supplied defaults are research candidates selected after viewing historical exports, not out-of-sample optimization results.
