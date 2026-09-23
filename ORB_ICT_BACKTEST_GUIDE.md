# ORB + ICT Backtest Strategy v1

## Purpose

`ORB_ICT_Backtest_Strategy_v1.pine` converts the confirmed-bar ORB logic from the existing ORB + ICT indicator and Markdown framework into a TradingView strategy. It is designed to compare XAUUSD and major forex pairs under the same rules. It does not modify or replace the indicator.

The strategy supports three entry models:

1. **Close breakout** — a confirmed strong candle closes outside the frozen ORB.
2. **Break + retest** — the qualified break must be followed by a boundary retest/rejection.
3. **Full framework** — the original mandatory sequence: preceding-range liquidity sweep, reclaim/reversal, strong ORB break, retest/rejection, then continuation.

Use these as separate experiments. Do not mix their CSV results into one sample.

## Starting TradingView settings

The script defaults to:

- Initial capital: **ZAR 10,000**.
- Base currency: **ZAR**.
- Long leverage: **500:1**.
- Short leverage: **500:1**.
- Equivalent margin requirement: **0.2%**, because `1 / 500 × 100 = 0.2%`.
- Risk per trade: **1% of current equity**.
- Pyramiding: off.
- Order timing: signal at confirmed close, market fill at the next available bar open.
- Slippage: 1 tick.
- Commission: 0% until you replace it with the broker's model.

Leverage is a ceiling, not the chosen risk. The strategy calculates quantity from the distance between entry and stop so that the planned stop loss is approximately the selected percentage of equity, then caps the quantity at the maximum exposure permitted by the leverage setting.

After adding the strategy, open **Settings → Properties** and confirm:

- **Initial capital:** 10000
- **Base currency:** ZAR
- **Long leverage:** 500:1
- **Short leverage:** 500:1
- **Commission:** match the broker/feed if applicable
- **Slippage:** set a conservative tick estimate for the symbol/feed
- **Order execution delay:** next bar, not on bar close

If TradingView shows margin percentages instead of leverage, use **0.2%** for long and short. If you change the leverage in Properties, change **Exposure cap leverage** under Inputs to the same value.

## Recommended first tests

Use standard candles. Do not use Heikin Ashi, Renko, or other synthetic charts.

| Test | Symbol | Chart | ORB session | ORB | Entry model | Validation | Stop | Target |
|---|---|---:|---|---:|---|---|---|---:|
| 1 | XAUUSD | 5m | New York | 30m | Break + retest | Standard | Opposite ORB | 2R |
| 2 | XAUUSD | 5m | New York | 30m | Full framework | Standard | Opposite ORB | 2R |
| 3 | EURUSD | 5m | London | 30m | Break + retest | Standard | Opposite ORB | 2R |
| 4 | GBPUSD | 5m | London | 30m | Break + retest | Standard | Opposite ORB | 2R |
| 5 | USDJPY | 5m | Asian | 30m | Break + retest | Standard | Opposite ORB | 2R |
| 6 | AUDUSD | 5m | Asian | 30m | Break + retest | Standard | Opposite ORB | 2R |

Also test USDCHF and USDCAD manually. Auto session mapping intentionally sends EUR/GBP/CHF pairs to London, JPY/AUD/NZD-led forex pairs to Asian, and metals/other symbols to New York. Override it when your trading hypothesis calls for another session.

Keep the following identical across pairs during the first comparison:

- date range;
- chart timeframe;
- entry model;
- validation mode;
- stop model;
- risk percentage;
- target R;
- commission and slippage assumptions;
- data vendor/broker feed where possible.

Change one variable at a time after the baseline comparison.

## What to compare

Do not rank pairs by net profit alone. Record:

- total closed trades;
- net profit in ZAR and percent;
- profit factor;
- maximum drawdown in ZAR and percent;
- percent profitable;
- average trade;
- average winning and losing trade;
- largest losing trade;
- margin calls, if any;
- buy-and-hold comparison where relevant;
- the exact symbol/feed, timeframe, session, date range, and input preset.

A small sample can look excellent by chance. Treat fewer than roughly 100 trades as preliminary and compare at least one in-sample period with a later, untouched out-of-sample period.

## Exporting results for review here

TradingView exports each Strategy Report tab separately.

For every symbol/preset:

1. Open **Strategy Tester / Strategy Report**.
2. Open **Performance Summary** and click **Download**. Save the CSV.
3. Open **List of Trades** and click **Download** again. Save that CSV too.
4. Take one screenshot of **Properties** and one screenshot of the strategy **Inputs**.
5. Rename files before uploading, for example:
   - `XAUUSD_5m_NY_30m_retest_standard_performance.csv`
   - `XAUUSD_5m_NY_30m_retest_standard_trades.csv`
   - `XAUUSD_5m_NY_30m_retest_standard_settings.png`

Upload the CSV files and settings screenshots here. With those files, the analysis can compare expectancy, drawdown, stability by period, long-versus-short behavior, session behavior, losing streaks, stop/target efficiency, and whether a modification improves out-of-sample results rather than only fitting past data.

## Important limitations

- The strategy is a research model, not a recommendation or guarantee.
- TradingView's broker emulator does not reproduce dynamic spread, variable slippage, financing, swaps, news-event gaps, partial fills, or every CFD contract rule.
- Quantity semantics depend on the symbol/feed. Check `Last planned quantity` and `Last required leverage` in the Data Window, then compare one sample trade with the broker's contract specification.
- ZAR conversion uses TradingView's account-currency conversion data and can differ from a broker's conversion rate.
- A 5-minute chart is the preferred baseline. The chart timeframe must not exceed the ORB duration and should divide the ORB duration evenly.
- The default one-tick slippage is only a placeholder. XAUUSD normally needs a feed-specific assumption.
- Static file checks do not prove TradingView compilation. Paste the source into TradingView and resolve any compiler message against the exact reported line before relying on results.

## Validation performed on 31 August 2026

The exact delivered local source compiled successfully in TradingView Pine v6 and opened the Strategy Report. A smoke test on the existing **FXCM EURUSD 30-minute** chart, **2 January to 31 August 2026**, using the default **Break + retest / Standard / 2R** settings produced 85 closed trades, ZAR 315.53 total P&L, ZAR 851.58 maximum drawdown, 42.35% profitable trades, and a 1.081 profit factor.

That smoke test proves the strategy compiled, generated orders, used the ZAR 10,000 account, and populated Strategy Report. It does **not** establish that EURUSD is profitable or that the settings are robust. The chart timeframe was 30 minutes rather than the preferred 5-minute baseline, the test period was short, and the model still used placeholder trading costs.
