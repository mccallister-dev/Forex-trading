# SMC Context Companion v1

## v1.5 — chart-structure agreement

**Pullback: require chart structure alignment** now defaults on. A continuation signal is blocked unless the latest confirmed chart BOS/CHoCH direction agrees with the selected HTF direction. For example, an H1/H4 bullish state cannot produce a BUY while the M5 structure state is bearish. Turning this filter off deliberately restores HTF-only behavior.

The context label now includes the chart-timeframe structure state. HTF direction is still based on the last confirmed HTF swing break and can lag a fast selloff; it should not be read as a real-time trend claim. When chart structure and HTFs disagree, the label is neutral and the default continuation model waits.

## v1.4 — HTF pullback continuation

**HTF pullback continuation** is now the default setup model. It addresses trend-following opportunities such as selling a confirmed pullback into supply while the selected higher timeframes are bearish. It does not require a new liquidity sweep before every entry.

The confirmed sequence is:

1. Determine direction from **Both HTFs agree** (default) or **HTF 2 only**, then require the confirmed chart structure to agree by default.
2. Wait for price to overlap an already-active, same-direction chart OB or FVG. The zone must have existed before the signal candle; a zone cannot signal on its creation bar.
3. Require an enabled engulfing or rejection candle in the HTF direction.
4. Optionally require a same-direction chart BOS/CHoCH and/or displacement on that confirmation candle.
5. Estimate entry at the confirmation close, SL beyond the zone edge plus the pullback ATR buffer, and TP at the selected reward/risk multiple.

The model calculates the internal OB/FVG zones required for signals even when their display toggles are off. Each zone can issue at most one pullback signal. **Pullback signal window** selects Opening windows, Full sessions or Any time. Full sessions default to 480 minutes from each configured London/New York start; overlapping windows use New York priority. **Maximum setups per signal window** defaults to two.

For the stricter original behavior, choose **Setup model = Sweep reversal**. Its sweep, displaced shift, HTF1 POI and optional confirmation sequence remains separate and unchanged.

## v1.3 — configurable opening-window capacity

The signal layer can allow one to three sequential qualified candidates per signal window. To reproduce the original one-shot behavior, choose **Sweep reversal**, set **Maximum setups per signal window = 1**, and leave **Sweep model: replace invalidated candidate = Off**. Sweep candidates remain strictly sequential; the script never holds two active candidate boxes at once.

## v1.2 — filtered SMC BUY / SELL plans

The indicator now has an optional **06 | SMC buy/sell signals** layer. It remains an indicator: it places no orders, sizes no broker position and is not a Strategy Tester script.

The Sweep reversal sequence follows the attached entry guide mechanically: opening-window liquidity sweep, later displaced structure shift, a newly created chart-timeframe FVG, optional confirmed HTF1 POI interaction, and optional HTF alignment. Candidate capacity is configurable from one to three per configured London or New York opening window; only one candidate can be active at a time.

Choose the signal model and gates in Inputs:

- **Sweep-reversal Risk entry** issues on the displaced structure-shift close and estimates an entry at the FVG open boundary or FVG 50%. SL is beyond the sweep extreme plus the configured ATR buffer; TP is the selected R multiple.
- **Sweep-reversal Confirmation entry** waits for a later return to the entry zone and then requires an enabled engulfing and/or rejection candle. Entry is estimated at that confirmation close; SL remains beyond the sweep; TP uses the selected R multiple.
- **Maximum setups per signal window** is a hard limit from 1–3. Pullback signals consume the quota directly; sweep candidates consume slots when created.
- **Sweep model: replace invalidated candidate** returns a sweep slot only when its candidate fails before producing a signal. It does not apply to direct pullback-continuation confirmations.
- Checkboxes independently control HTF1 OB/FVG interaction, H1/H4 alignment, displacement FVG, engulfing and rejection. If both confirmation-candle checkboxes are off while Confirmation entry is selected, no confirmation signal can qualify.
- BUY/SELL markers and entry/SL/TP line colours are customizable. Plans remain drawings only. A later level touch updates the caption; if SL and TP occur inside the same chart candle, the result is reported as both touched rather than guessed.

The H1 POI, OB, FVG, sweep, structure and candle tests are objective proxies described in this guide; they are not a claim to reproduce a discretionary or proprietary SMC method. Pine has no built-in economic-calendar release filter in this script, so the guide's high-impact-news avoidance remains a manual check.

## v1.1 — optional session-entry candidates

The chart title is now **SMC Sessions**. The source stays in `SMC_Context_Companion_v1.pine`; the prior source/guide are preserved in `Backups/2026-09-18-before-smc-session-zones/`.

Under **05 | Session entry candidates (optional)**:

- **Show possible session entry zones** enables one faint candidate box at most, independent of the ordinary OB/FVG display toggles.
- **Highlight session starts** is a separate toggle. Choose **Start bar only** (minimal) or **Opening window** (faint background).
- Each session has an enable toggle, start hour, minute and timezone. Defaults: London 08:00 `Europe/London`, New York 08:00 `America/New_York`, 60-minute opening windows. These are local session times, NOT your chart's South African clock. IANA timezones follow DST. You may instead use `Africa/Johannesburg` with your desired fixed SAST hour.
- Use start times and durations aligned to M5 bars. Only bars entirely inside the opening window qualify. The highlight starts on the first eligible chart bar, not an invented bar at a missing timestamp. Weekdays use the local opening date; overnight windows are supported. If customized windows overlap, NY takes priority for candidate state.
- **Candidate direction filter** defaults to **Both HTFs agree**. H4 only means the configured Higher timeframe 2 (default H4); Unfiltered is for inspecting all candidate directions, not a recommendation. Mixed H1/H4 means no candidates under the default filter.

### Exact candidate sequence

1. A confirmed one-sided liquidity sweep must occur inside the opening window. Both-sided sweeps do not arm a setup. Freeze the opposing, existing unbroken swing as the structure trigger and the sweep extreme plus the configured ATR buffer as invalidation.
2. A LATER candle must close beyond that frozen swing using the existing structure buffer. Its body must meet the existing displacement criteria. This can be a chart CHoCH or BOS; the candidate does not require the chart's prior bias to be opposite.
3. Search for the nearest opposing-colour candle from the sweep candle through the candle before the break, bounded by the existing OB lookback. Use the selected full-candle/body bounds. The break must close beyond that zone. If no qualifying candle exists, no box appears. FVG selection is NOT part of this first candidate layer.
4. The box starts at the confirming candle's closing timestamp, never retrospectively at the sweep/source candle. It says **LDN/NY possible buy/sell**. A later overlap makes its border dashed; that touch alone is NOT entry confirmation.

The first close through the frozen trigger consumes the pending setup even if displacement/zone checks fail. Pending setups expire after the configurable bar limit, at window end, on buffered sweep invalidation or loss of the chosen HTF alignment. A fresh later sweep can arm another attempt while capacity remains. Candidate slots and replacement after invalidation follow the v1.3 controls above.

An existing candidate is removed at window end, on a wick touching buffered sweep invalidation, a close through the zone's far edge, or loss of required HTF alignment. Candidate extension is capped at window end. No candidate is created at the last bar's closing boundary because there is no remaining in-window retracement time. This lifecycle is separate from ordinary OB/FVG removal settings. Disabling the feature removes its candidate. When a candidate forms over an identical ordinary OB, that ordinary OB is removed to avoid duplicate captions; it is not restored when the candidate later expires.

Only the current active candidate box is retained: use Bar Replay to inspect previous openings. The faint session background remains historically visible. As of v1.2, the separate optional signal layer can add BUY/SELL markers, estimated entry/SL/TP drawings and alerts; it still adds no trades or dashboard.

**Scope limitation:** both setup models use objective chart/HTF proxies, not a complete discretionary SMC method. Pullback continuation validates an active chart OB/FVG and candle confirmation, but it does not currently require premium/discount eligibility, quantify room to opposing liquidity, or consume a live economic calendar. Those remain manual checks. No signal appearing is a valid outcome; do not loosen settings merely to force one.

Session/time behavior follows [TradingView's session documentation](https://www.tradingview.com/pine-script-docs/concepts/sessions/).

Created 17 September 2026. A separate Pine v6 **indicator**, not a Strategy Tester strategy, trade executor, or extension of the ORB scripts. No dashboard. No SL/TP, lot sizing or automatic ORB acceptance/rejection. Existing ORB files are unchanged.

## Start here

1. Open a **standard M5 candle chart**, initially your existing XAUUSD feed.
2. Create a **new indicator** in TradingView's Pine Editor. Do not replace your ORB script or an unsaved draft.
3. Paste the complete `SMC_Context_Companion_v1.pine`, compile, and add it to the chart. Save it under its own name.
4. Leave the context inputs at **H1 (60)** and **H4 (240)**. Both must be higher than the chart interval. An explicit runtime message rejects unsupported timeframes or synthetic chart types.
5. Display SMC alone first to learn the marks, then show your ORB indicator alongside it. Keep the same symbol/feed, interval and historical window.
6. Pin both overlays to the **same price scale as the candles**. A No-scale/different-scale setting can make drawings appear detached when dragging the chart.

The exact local source was pasted, read back and matched, then compiled successfully in signed-in TradingView on 17 September 2026. Live rendering and optional-layer recalculation were inspected on FXCM XAUUSD M5. On 18 September, after an account change removed the intraday replay restriction, a short M5 Bar Replay smoke test also completed. These checks validate basic execution, not profitability or exhaustive non-repainting behavior. No alerts have been activated.

## What the clean default view shows

| Mark | Meaning | Default |
|---|---|---|
| One small label beside current price | H1/H4 structural direction, agreement/conflict and latest closed chart price's location in the selected HTF range | On |
| Three short HTF lines | Latest confirmed swing high, 50% midpoint and swing low; H4 selected initially | On, no fill |
| CHoCH up/down | Close through an opposing confirmed chart swing relative to the prior chart direction | On |
| High swept / Low swept | Wick exceeds an existing chart swing and the same candle closes back inside | On |
| Demand OB / Supply OB | Mechanical chart-timeframe order-block proxy created on a displaced structure break | One latest active zone per direction |
| BOS / Initial break | Same-direction structure continuation / first direction established | Off |
| FVG boxes | Qualified chart-timeframe three-candle price gaps | Off |
| Latest unswept swing levels | Two additional chart-timeframe liquidity references | Off |
| Demand / Supply reaction | Optional confirmed rejection of an existing zone, not a buy/sell instruction | Off |

Default retention is **three observed trading days**, today plus the two previous days represented in chart data, using Africa/Johannesburg. Weekends without chart bars do not consume a day. Historical marks also have a **24-event cap**. Zones have a **150-chart-bar age limit**, the same day retention, and per-type/per-direction caps. The earliest limit wins; still-valid old zones can disappear because of retention/caps. The source does not claim a historical mark was invalid simply because its drawing aged out.

The live context label and latest HTF range are current-state references, not historical event records. They update as the state changes. The HTF range is shown for at most 80 chart bars, and only from when its current pair was known; it is never projected backwards over earlier candles. Its right extension and zone extensions are display space, not forecasts.

## Exact mechanical definitions

### 1. Confirmed swings and direction

- A swing high has the configured number of bars on both sides; a swing low is the inverse. The default is **3 left / 3 right**.
- This deliberately introduces confirmation delay: on M5, three right bars take 15 minutes; on H4, three right bars take 12 hours. Those peaks were not available to the algorithm at the moment they formed.
- All chart events are evaluated at candle close, using previously available levels. Newly confirmed pivots are admitted only after that evaluation, so they cannot be swept/broken on their own confirmation bar.
- Structure changes when a close exceeds a confirmed high/low by **0.05 ATR**, minimum one tick. ATR is 14 bars in the relevant timeframe. Each swing can break only once until a new confirmed swing replaces it.
- The first close break establishes direction and is labelled Initial break if BOS display is enabled. A same-direction break is BOS. An opposite-direction break is CHoCH. **Displacement is not required for the structure label itself.**
- Chart swing levels expire 300 chart bars after confirmation. HTF direction remains the last confirmed swing-break direction until the opposite break; it has no time-based expiry.
- Both HTFs use the same swing rule, evaluated independently in their own source timeframes. Every requested value is offset by one source bar with `lookahead_on`, so only completed HTF data is used. There is no developing-H4 preview masquerading as confirmed bias.
- H1 bullish and H4 bearish means **mixed**, not a forced buy or sell. If either has not established direction, the combined status is also unconfirmed/mixed.

These are **latest-confirmed-pivot rules**, not inducement-qualified major/minor structure, a protected-high/low algorithm, or an EMA proxy. A CHoCH here is a defined structural event, not proof that the trend will reverse.

### 2. HTF range, premium and discount

The reference range is the latest confirmed swing high and swing low of the selected HTF. It is displayed only if high > low. The midpoint is `(high + low) / 2`.

- Above midpoint but inside range: Premium.
- Below midpoint but inside range: Discount.
- Outside the bounds: Above range / Below range, rather than pretending the range still contains price.

The latest high/low pair is a **range proxy**; it is not guaranteed to be the discretionary dealing range that you or a creator would select. Premium does not automatically mean sell; discount does not automatically mean buy. The price-location caption uses the last closed chart candle, not a flickering intrabar price.

### 3. Liquidity sweeps

- High swept: trades more than **0.05 chart ATR** above the last confirmed unswept/unbroken swing high, then closes **below the high** on the same candle.
- Low swept: trades more than the buffer below the swing low, then closes **above the low**.
- Minimum distance is one tick. Each level can emit only one sweep. A wide candle can sweep both sides; the script records both without inventing a directional preference.
- A sweep marker is not a reversal signal. There is no equal-high/low clustering or session-liquidity model in this version.

### 4. Order-block proxies: chart timeframe only

On a structure-break candle with directional displacement, search back at most **12 candles**, no earlier than the latest confirmed opposing swing's origin, for the nearest opposing-colour candle.

Displacement requires a body of at least **0.60 ATR** and at least **50% of the candle's full range**. A bullish break searches for a bearish candle; a bearish break searches for a bullish candle. The break must close beyond the selected candle's zone. No suitable candle means no OB box.

The box uses the source candle's full high/low by default; Body only is selectable. It starts visually on the **confirmation/break bar**, not the old source candle. This prevents hindsight appearance of a known zone before the confirming break. Bullish zones are labelled Demand OB and bearish zones Supply OB; those labels describe the model, not verified institutional orders.

### 5. FVGs: chart timeframe only, optional

Bullish FVG: the third candle's low is above the first candle's high. Bearish FVG: the third candle's high is below the first candle's low. The middle candle must have directional displacement, and the gap must be at least **0.05 ATR**, minimum one tick. The gap is created only when candle three closes and its box begins there, not two bars back.

### 6. Zone lifecycle and optional rejection marks

Zones cannot touch/mitigate themselves on their creation bar. A later overlap makes the surviving box border dashed. Choose removal behavior:

- **Close through far edge** (default): demand removed on close below its bottom; supply removed on close above its top. A wick through it alone is allowed.
- **Wick reaches far edge**: remove when price reaches/passes that far boundary. No rejection event is emitted from that breached zone on that candle.
- **First touch**: remove on any overlap, but a valid rejection on that first touch can still be recorded before deletion.

Optional demand rejection: later candle overlaps the zone, is bullish and closes **above its top**. Supply rejection: overlaps, is bearish and closes **below its bottom**. Only one accepted reaction per zone. Expired/close-invalidated zones cannot react. A surviving zone's first touch need not be its first qualifying rejection.

With **Annotate only**, these marks include the HTF context but are not filtered by it. With **Both HTFs agree**, demand requires both HTFs bullish and supply requires both bearish. This switch affects optional rejection marks only—not structural evidence or zone visibility. No liquidity sweep is required before a rejection in this version.

## Comparing against ORB without combining the scripts

An ORB sell near an existing demand zone, in discount, while both HTFs are bullish is a **context conflict to inspect**. It is not automatically invalid or guaranteed to lose. An ORB buy can similarly conflict with bearish HTF structure or nearby supply.

At the peaks in your screenshot, a sweep, supply zone or bearish structure change might provide context **only if it was already confirmed at that time**. This indicator does not label every eventual top as an earlier sell opportunity. Later-confirmed H4 pivots and newly created zones must not be used to justify a trade retrospectively.

Use Bar Replay from before the area of interest. Record what was visible when the ORB signal actually printed, not what is visible after the full move. The small H1/H4 label and latest range show the replay endpoint's state; don't apply today's endpoint label to an older ORB signal.

For an uncluttered first comparison, leave BOS, FVGs, range fill, liquidity levels and reaction marks off. Hide unrelated older indicators. You can switch off the single context label too; the two direction values remain in the Data Window.

## Reference scope and limits

You supplied [HANNAH FOREX](https://www.youtube.com/@HANNAHFOREX/videos) and [TRADiNG hub](https://www.youtube.com/@TRADiNGhub/videos). Their channel pages were checked, but a specific original lesson/transcript was not verified. This script is **not a verified implementation or endorsement of either creator's strategy**, nor a copy of the licensed reference script in the workspace. A particular lesson and timestamps are needed before claiming its inducement, protected-swing, POI or entry rules are reproduced.

Technical implementation references:

- [TradingView: confirmed higher-timeframe data](https://www.tradingview.com/pine-script-docs/faq/other-data-and-timeframes/).
- [TradingView: repainting and confirmation tradeoffs](https://www.tradingview.com/pine-script-docs/concepts/repainting/).
- [TradingView: drawing objects](https://www.tradingview.com/pine-script-docs/visuals/lines-and-boxes/).

## Validation and maintenance

- `tools/test_smc_context.py`: 24 passing source-guard and independent Python rule-model tests at delivery. These do **not** run the Pine engine or prove compilation.
- Tests cover initial/BOS/CHoCH classification, repeated-break suppression, same-bar pivot ordering, both-sided sweeps, zone mitigation/rejection combinations, observed-day retention and ORB source integrity.
- Default historical object limits are 24 event lines/labels plus two OB boxes, the latest three HTF range lines and one context label. Optional categories are bounded below the declaration's object limits.
- TradingView compilation and a limited live/replay visual smoke test passed; see `SMC_VALIDATION_2026-09-18.md`. Alert delivery, source-feed comparisons, long-history replay and exhaustive reload/non-repainting checks remain unverified. No performance backtest or profitability claim exists for this context indicator.
- Pre-existing ORB sources were copied to `Backups/2026-09-17-before-smc-companion/`; their hashes remain unchanged.

Run local checks using `python3 -m unittest discover -s tools -p test_smc_context.py -v`. Edit this standalone Pine file directly; it is not part of the ORB generator. Recompile and inspect replay after changes. If you later create alerts, use once-per-bar-close and recreate them when source/settings change. Alert notifications are not required for drawings.
