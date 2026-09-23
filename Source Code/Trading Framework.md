# ORB + ICT Session Liquidity Framework

## Deliverables

- `ORB_ICT_Session_Liquidity_Framework.pine` — complete Pine Script v6 overlay indicator.
- This guide — installation, settings, logic, presets, limitations, and repaint audit.

The script was compiled successfully in TradingView's Pine v6 editor on 5 August 2026 and added to an EURUSD 30-minute chart.

## Installation

1. Open a TradingView chart.
2. Open **Pine Editor** at the bottom of the chart.
3. Choose **Create new → Indicator**.
4. Replace the example code with the full contents of `ORB_ICT_Session_Liquidity_Framework.pine`.
5. Select **Add to chart**.
6. Save the script in TradingView if you want it available in **My scripts**.

For ORB and sweep work, use a standard candle chart. Five-minute and 15-minute charts are the practical defaults. Heikin Ashi, Renko, and other synthetic charts feed synthetic OHLC prices to the script and therefore change every level and condition.

## Settings guide

### Sessions

Enables Asian, London, New York forex, New York equity, and two custom sessions. Each session has an editable session string, named timezone, colour, transparency, width, style, label size, and extension mode. The common display switches control backgrounds, vertical boundaries, names, OHLC, midpoint, and range boxes. Named IANA zones handle daylight-saving changes; the chart timezone is not used for calculations.

### Opening Ranges

Enables Asian, London, New York forex, New York equity, and Custom 1 ORBs. Choose 5, 15, 30, 60, or custom minutes. High, midpoint, low, open, and close form only during the range window, then freeze. Pip mode can be Auto, 0.0001, 0.01, or a custom value. Non-forex symbols display raw range size.

### Timeframe Roles

Maps the actual chart timeframe to Macro, Bias, Range, Entry, Precision Entry, or a user-edited role. The mapping can appear in a table and in level labels. Internally requested timeframes never replace the chart timeframe shown in these labels.

### Key Levels

Shows completed previous-day and previous-week highs/lows, current daily open, New York calendar-day open, completed Asian range, and frozen London/New York ORBs. The history setting retains a bounded number of drawing objects. Colours are separated by weekly, daily, open, session, and ORB category; line/label styling is shared to keep the input panel and object budget manageable.

### Fair Value Gaps

Controls confirmed 1H and 4H three-candle FVGs, minimum gap size, displacement qualification, mitigation definition, fill behaviour, and retention. **Any** displacement logic accepts body, range, or close-location qualification; **All** requires all three. Boxes can stop at mitigation, extend indefinitely, dim after a partial fill, or be removed after full fill.

### Liquidity

Uses confirmed pivots to cluster approximate equal highs/lows. Tolerance is the greater of the tick allowance and ATR percentage. Choose two or three touches, separation limits, wick/close sweep confirmation, swept styling, and retention.

### Bias Engine

Weights daily/NY-open alignment, confirmed 1H/4H structure proxy, previous-day and Asian sweeps, active FVG reactions, and displaced ORB breaks. It reports bullish, bearish, and net confluence scores. This is a classification, not a profitability prediction.

### Setup Detection

Select London using Asian range, New York using the London range snapshot, or Custom 1 using Asian/London. Configure sweep, reclaim, displacement, ORB break, retest, rejection, continuation, expiry, invalidation, and score weights. Bullish and bearish sequences are tracked independently. **Confirmed bars only** should remain enabled for stable signals and alerts.

### Target Space

Estimates reward/risk from the signal close to the nearest enabled structural target, using a stop at the sweep extreme or retest swing. It is an analytical filter only and never places an order.

### Dashboard

Displays symbol, chart timeframe/role, active session, ORB states, sweeps, bias and setup scores, current sequence stage, target space, nearest FVG, and nearest unswept liquidity.

## Objective setup logic

### Session sweep

- Bearish: price trades at least the configured tolerance above the frozen preceding-range high.
- Bullish: price trades at least the tolerance below the frozen preceding-range low.
- The selected mode can accept the wick, require the same candle to close back inside, or wait for a later reclaim.

### Reversal

The script applies **Any selected** or **All selected** to: close back through the liquidity level, close through the sweep-candle midpoint, opposite-colour displacement, confirmed short-pivot break, and cross back through liquidity.

### Displacement

A directional candle must pass the selected combination of body greater than ATR × multiplier, range greater than ATR × multiplier, minimum body percentage, close near the directional edge, confirmed short-swing break, and same-direction chart FVG.

### ORB break

The selected ORB must be frozen. Default confirmation is a close beyond the boundary by the minimum tick distance, within the maximum ATR distance, with directional displacement. Wick mode is optional.

### FVG

- Bullish: the completed higher-timeframe candle's low is above the high two source candles earlier.
- Bearish: the completed higher-timeframe candle's high is below the low two source candles earlier.
- A new box is emitted only when the source 1H/4H candle is completed and the configured size/displacement/bias filters pass.

### Retest and rejection

A retest must occur after the breakout bar and within the configured bar limit. It can touch the broken ORB boundary, the breakout FVG midpoint, the prior-candle order-block proxy, or the chosen combination. Rejection can require a close back beyond the ORB, rejection wick, engulfing candle, and/or confirmed short-term structure break.

### Continuation

After rejection, bullish continuation requires a later confirmed close above the most recent confirmed short-term pivot high. Bearish continuation requires a later confirmed close below the most recent confirmed short-term pivot low.

### Invalidation and expiry

Optional rules invalidate a developing sequence on a close beyond the sweep extreme, close through the opposite ORB boundary, missed retest deadline, opposite displacement/structure break, session end, or maximum bars since sweep. A separate setup-expiry limit is also applied. Once a confirmed signal label prints, later bars do not remove it.

### High-quality classification

The permanent high-quality label requires both:

1. completion of the mandatory sweep → reversal → ORB break → retest/rejection → continuation sequence; and
2. a score at or above the high-quality threshold, plus the target-space requirement when that filter is enabled.

A high score alone cannot create a high-quality signal.

## Recommended starting presets

### EURUSD — London ORB

- Chart: 5M or 15M standard candles.
- Asian: 00:00–08:00 Europe/London; London: 08:00–16:00 Europe/London.
- London ORB: enabled, 30 minutes; pip size: Auto.
- Setup context: London using Asian range; confirmed bars only: on.
- Sweep tolerance: 1 tick; retest tolerance: 3 ticks.
- Displacement: body 1.0 ATR, range 1.2 ATR, body 60%, close-near 20%, Any selected.
- ORB break: candle close; minimum 1 tick; maximum 5 ATR.
- Retest: ORB or FVG midpoint, within 20 bars.
- Target filter: start disabled for observation, then enable at 3R after symbol-specific review.

### EURUSD — New York ORB

- Chart: 5M or 15M standard candles.
- New York forex: 08:00–17:00 America/New_York; ORB: 30 minutes.
- London session enabled so its range can be snapshotted at the New York open.
- Setup context: New York using London range; confirmed bars only: on.
- Use the London-preset displacement and tolerance defaults.
- Enable NY midnight open and previous-day levels.
- Review broker feed alignment around 08:00 New York before enabling alerts.

### XAUUSD — New York ORB

- Chart: 5M standard candles.
- New York forex: 08:00–17:00 America/New_York; ORB: 30 minutes. For a cash-equity-driven study, use the editable 09:30 equity session instead.
- Pip mode: Auto so labels use raw range units; do not force forex pip assumptions.
- Sweep tolerance: 3 ticks; retest tolerance: 5 ticks, then tune for the broker's tick size.
- Displacement: body 1.2 ATR, range 1.3 ATR, body 60%, close-near 20%.
- FVG minimum: Either, 5–10 ticks and 5% ATR as a starting filter.
- Target filter: 3R; structural stop: sweep extreme.

## TradingView and timeframe limitations

- Session and ORB boundaries are resolved from chart bars. A 5-minute ORB on a 15-minute chart necessarily uses the whole first 15-minute bar. Use a chart timeframe no larger than the ORB duration, ideally one that divides it evenly.
- If a bar straddles a session boundary, its open determines session membership. Session close is the close of the final chart bar whose opening time belongs to the session.
- The New York midnight open is the first available chart-bar open in the configured New York calendar day. On higher timeframes or feeds without a bar at 00:00, it is not an exact tick at midnight.
- 1H FVGs are intended for charts at or below 1H; 4H FVGs are intended for charts at or below 4H. TradingView's ordinary `request.security()` returns only one lower-timeframe bar when the requested timeframe is below the chart timeframe.
- The 1H/4H structure component is an objective confirmed-close versus 50-EMA proxy, not discretionary swing interpretation.
- “Lower-timeframe structure shift” uses confirmed pivots on the current chart timeframe. The script deliberately avoids lower-timeframe requests for performance and stability.
- `alertcondition()` messages must be compile-time strings. Symbol and chart timeframe use TradingView placeholders; the live score and exact levels remain in the dashboard/signal label.
- Drawing retention is capped by internal per-category budgets so the script stays below TradingView's global 500-line, 500-label, and 300-box limits. With many categories enabled simultaneously, the oldest objects can be removed before a requested 20-period maximum.
- Overlapping enabled sessions can layer background colours and objects.
- Target space is structural geometry, not a fill, slippage, spread, or execution model.

## Repainting and future-data audit

- Previous day/week: `high[1]` and `low[1]` are requested with `lookahead_on`, so only the last completed period is projected into the new period.
- Current daily open/time: requested with `lookahead_on`; these values are known at the first instant of the current daily period and remain fixed, so no unknown daily high/low leaks forward.
- 1H/4H FVG: all source values are offset to completed HTF bars; a box is created only when the completed HTF timestamp changes.
- Equal highs/lows: `ta.pivothigh()`/`ta.pivotlow()` emit only after the configured right bars have elapsed.
- Sessions: high/low/close update while active and stop changing after the final in-session bar.
- ORBs: values update only before the timestamped ORB deadline, then remain frozen until the next selected session.
- Setup transitions and alerts: with **Confirmed bars only** enabled, all permanent transitions require `barstate.isconfirmed`.
- Permanent setup labels: created once on continuation confirmation and never revised or deleted by later invalidation logic, except oldest-label cleanup under the configured retention budget.
- Developing status: one reused last-bar label can update intrabar only when confirmed-only mode is disabled, and is marked **PROVISIONAL**.
- No negative history offsets, future bar indices, or unoffset higher-timeframe highs/lows are used.

Official Pine references used for the implementation: [Sessions](https://www.tradingview.com/pine-script-docs/concepts/sessions/), [Time](https://www.tradingview.com/pine-script-docs/concepts/time/), [Other timeframes and data](https://www.tradingview.com/pine-script-docs/concepts/other-timeframes-and-data/), and [Alerts](https://www.tradingview.com/pine-script-docs/concepts/alerts/).
