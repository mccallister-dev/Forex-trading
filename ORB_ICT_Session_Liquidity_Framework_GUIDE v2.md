# ORB + ICT Session Liquidity Framework

## What this indicator is

This Pine Script v6 overlay is a non-repainting observation framework for three major sessions, one selected opening range, directional ORB validation, and a mandatory liquidity-to-continuation setup sequence. It is designed for forex, metals, indices, CFDs, and other symbols with regular intraday bars.

The framework reports analytical observations only. A bias score is evidence balance, a setup score is confluence quality, and neither is a probability, win rate, confidence percentage, or trade recommendation.

## First use

1. Select a 5-minute or 15-minute standard candle chart.
2. Leave **Display mode** on **Minimal**.
3. Choose the relevant ORB session, or leave **ORB session** on **Auto**.
4. Observe the ORB move through **Upcoming**, **Forming**, and **Closed**.
5. Wait for confirmed validation stages. A high score cannot bypass the required sequence.
6. Treat every output as an analytical observation, not an instruction to trade.

## Installation

1. Open a TradingView chart and choose **Pine Editor**.
2. Create a new indicator.
3. Replace the sample code with `ORB_ICT_Session_Liquidity_Framework.pine`.
4. Choose **Add to chart**.
5. Save the script in TradingView if you want it in **My scripts**.

The delivered source was compiled successfully in TradingView's Pine v6 editor on 20 August 2026 and added to a GBPJPY 30-minute chart. For actual ORB observation, use a 5-minute or 15-minute chart whenever possible.

## Display modes

### Minimal

Minimal is the default. It draws light, border-focused Asian, London, and New York boxes with one small session name; a compact selected ORB box; the ORB-close icon; short ORB high/low segments; and the compact dashboard. It does not draw Imbalances, Equal highs/lows liquidity, or previous-day/week levels.

### Standard

Standard retains the clean session, ORB, marker, setup, and dashboard presentation with slightly stronger session and ORB fills. Optional technical zones remain suppressed so the chart stays readable.

### Analysis

Analysis permits the optional **Imbalance**, **Equal highs/lows**, and **previous-day/week** layers when their Advanced switches are enabled. Each optional zone category is capped by **Maximum visible zones**. Filled Imbalances are removed, partly filled Imbalances are faded, and swept Equal highs/lows stop extending and fade.

### Custom

Custom uses the same clean internal style system but permits the Advanced technical switches and provisional developing label. Repeated widths, line styles, label sizes, separate OHLC lines, and indefinite extensions are deliberately not exposed.

## Trading-day retention

**Trading days to display** retains the current day plus the immediately preceding chart days that actually contain bars. With a value of 3, the framework keeps the current trading day and the two previous trading days.

Each drawing is tagged with a stable `yyyyMMdd` key in the selected display timezone. When a fourth trading day begins, objects tagged with the oldest retained key are deleted. Weekends and missing market days with no chart bars are not counted, so the setting is not an arbitrary session/object multiplier.

Independent internal caps also keep drawings below TradingView's line, label, and box limits. Those safety caps do not change the meaning of the trading-day setting.

## Sessions and timezones

The defaults are:

- Asian: 00:00-08:00, `Europe/London`.
- London: 08:00-16:00, `Europe/London`.
- New York: 08:00-17:00, `America/New_York`.
- Custom: 06:00-10:00, Exchange timezone, disabled by default and available only under Advanced.

Every major session has an enable switch, editable session string, IANA timezone, and box color/transparency. Named zones such as `Europe/London` and `America/New_York` allow TradingView to apply daylight-saving changes. The chart timezone is a display preference and does not control Pine calculations.

**Display timezone** controls the dashboard clock and stable retention day key. It does not rewrite the independently configured session timezones.

## Preferred session and Auto mapping

**Preferred session mode** can be Auto or Manual. The preferred session is used by **ORB session: Auto** and is shown in the dashboard.

Auto normalizes `syminfo.root` and `syminfo.ticker`, which makes broker prefixes and common suffixes less important, then applies this deterministic mapping:

- Crypto: Asian.
- Forex containing EUR, GBP, or CHF: London.
- Other forex containing JPY, AUD, or NZD: Asian.
- Other forex, metals, indices, stocks, futures, and CFDs: New York.

The European-currency rule takes priority for crosses such as EURJPY. Unsupported or unusual broker symbols fall back to New York. Use Manual for a deliberate override.

If the requested ORB session is disabled, the indicator falls back to the first enabled session in this order: London, New York, Asian.

## ORB lifecycle

The selected opening range can be 5, 15, 30, 60, or a custom number of minutes.

1. **Upcoming** - the selected session's current-day ORB has not started.
2. **Forming** - high and low update from bars whose opening times fall inside the ORB window.
3. **Closed** - after the last constituent ORB bar is confirmed, high and low freeze permanently for that session/day.
4. **Break observed** - a confirmed candle closes outside the frozen range by at least the minimum tick distance and passes the Strong move test. Optional net-bias alignment may also be required.
5. **Retest** - a later confirmed candle retests the broken boundary and closes back on the breakout side. Strict mode also requires rejection-wick or engulfing evidence.
6. **Confirmed** - a later confirmed continuation close clears the retest candle's directional extreme. Strict mode also requires another Strong move.

The diamond icon is created once, on a confirmed bar, over or just above the ORB-completing candle. It is not recalculated later. The ORB box stops at the ORB deadline. After closure, only the high and low continue as short segments, and they stop at the associated session close. No default line extends indefinitely.

The ORB itself is neutral. Touching or crossing a boundary does not label the range bullish or bearish.

## Standard versus Strict validation

A qualified directional ORB observation always requires a confirmed close, minimum distance, and Strong move. A Strong move combines directional candle color, an ATR-relative body, a minimum body percentage, and a close near the directional edge.

- Standard uses a 0.75 ATR body and 50% body share, followed by a boundary retest/rejection and continuation.
- Strict uses a 1.0 ATR body and 60% body share, requires stronger reversal/rejection evidence, and requires Strong move qualification again on continuation.

**Confirmed bars only** defaults on. Permanent state transitions and permanent markers remain confirmed-bar only even if the setting is turned off. Turning it off merely permits the optional last-bar label, which is explicitly marked **PROVISIONAL** and is the only object allowed to move intrabar.

## Bias evidence and net bias

Bullish and bearish evidence are calculated separately from:

- current daily-open alignment;
- completed 1-hour close versus 50 EMA;
- completed 4-hour close versus 50 EMA;
- previous-day sweep and reclaim/rejection;
- Asian-range sweep and reclaim/rejection;
- reaction to the latest completed higher-timeframe Imbalance; and
- a qualified selected ORB break.

Net bias is:

`bullish evidence - bearish evidence`

Classifications retain the existing thresholds:

- Strong Bullish: +5 or higher.
- Bullish: +2 to +4.
- Neutral: -1 to +1.
- Bearish: -2 to -4.
- Strong Bearish: -5 or lower.

The dashboard shows both the net result, such as **Strong Bullish +5**, and the component totals, such as **7 bullish / 2 bearish**. This is an evidence classification, not a probability.

## Setup stage versus setup score

The permanent setup sequence is:

`sweep -> reclaim/reversal -> ORB break -> retest/rejection -> continuation`

Bullish and bearish candidates are tracked independently. The selected setup stage shows what must happen next, for example **ORB break pending** or **Retest / rejection pending**.

Setup quality keeps the existing 16-point maximum:

- sweep: 2;
- reclaim/reversal: 2;
- aligned net bias: 2;
- ORB break: 1;
- Strong move: 2;
- breakout Imbalance: 1;
- retest/rejection: 2;
- continuation: 2;
- target space of at least 2R: 1;
- active selected session: 1.

Quality labels are Low, Developing (5+), Good (8+), and High (11+). Stage and quality are independent. A high score alone never creates a confirmed marker; only completion of the mandatory sequence can do that.

Target space is a structural estimate from the confirmed close to the nearest eligible previous-day/week target relative to the sweep-extreme risk. It appears only after confirmation and does not model spread, slippage, execution, or fill probability.

## Compact dashboard

The dashboard has two columns and eight rows:

1. Symbol / pair.
2. Preferred session.
3. Current / next session and display-timezone clock.
4. ORB lifecycle.
5. Net bias classification and score.
6. Bullish and bearish evidence totals.
7. Setup direction and stage.
8. Setup quality, plus target space only after confirmation.

Use **Show dashboard** to hide it completely. **Preferred session** is intentionally used instead of “Best session” because the script does not perform historical performance measurement.

## Optional technical layers

The framework continues to calculate completed 1-hour/4-hour Imbalances needed for bias even when their boxes are hidden. Analysis and Custom modes can display the optional layers:

- **Imbalance (FVG):** completed 1-hour and 4-hour three-candle gaps; filled zones are removed and partly filled zones fade.
- **Equal highs/lows:** approximate matches of confirmed 3-left/3-right pivots using a three-tick-or-3%-ATR tolerance; swept levels stop and fade.
- **Previous levels:** completed previous-day and previous-week highs/lows.

User-facing labels use Imbalance, Equal highs/lows, Strong move, and Filled. The technical term is retained only in the FVG input tooltip/label for experienced users.

## Alerts

Four one-shot confirmed alerts are available:

- ORB closed.
- Confirmed ORB break.
- Retest/rejection confirmed.
- Final setup confirmed.

Dynamic `alert()` messages include symbol, selected session, direction where relevant, setup score, and net bias. Matching `alertcondition()` entries are also available in TradingView's Create Alert dialog. One-shot event flags and `alert.freq_once_per_bar_close` prevent repeated alerts for the same stage/bar.

## Non-repainting guarantees

- ORB values update only while Forming and freeze after the confirmed completion bar.
- The ORB-close icon and confirmed setup markers are created only on confirmed bars.
- Permanent markers are never moved or rewritten; they are removed only by trading-day retention or internal object safety caps.
- 1-hour and 4-hour structure use `[1]` completed-source values.
- 1-hour and 4-hour Imbalances use only completed source candles and are detected when the completed source timestamp changes.
- Previous-day/week levels use completed `[1]` values.
- Equal highs/lows use confirmed pivots after the right-side bars have elapsed.
- No negative history offset, future bar index, or unconfirmed higher-timeframe high/low is used.

## Unavoidable timeframe limitations

- Session and ORB boundaries resolve from chart bars. A 5-minute ORB on a 15-minute chart necessarily uses the first 15-minute candle. Use a chart timeframe no larger than the ORB duration, ideally one that divides it evenly.
- A bar belongs to a session when its opening time is inside the configured session. The final in-session bar determines the session box's right edge.
- Higher-timeframe data is intentionally delayed until the source candle closes.
- Standard candles are required for literal OHLC observations. Heikin Ashi, Renko, and other synthetic charts change the prices supplied to the script.
- Auto preferred-session mapping is deterministic symbol classification, not measured historical performance.

## Practical acceptance checklist

- Pine Script reports version 6 and compiles in TradingView.
- Minimal mode shows only clean session/ORB structure and the compact dashboard.
- Trading days = 3 keeps the current trading day plus the two preceding chart trading days.
- Asian, London, and New York hours and IANA zones are editable.
- ORB high and low stop changing after the confirmed close bar.
- One diamond appears for the selected ORB session/day.
- Permanent setup markers never appear intrabar.
- The dashboard can be hidden and remains within eight rows.
- No score is described as a probability.
- No default line extends indefinitely.
- Optional technical drawings are absent in Minimal mode.
