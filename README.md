# Forex Trading

Private TradingView research workspace for opening-range breakout (ORB), ICT-style context and mechanical SMC session analysis.

The repository contains Pine Script indicators and strategies, supporting research, reproducible source generators, validation tests and plain-language operating guides. It is intended for research and discretionary review—not automated execution or financial advice.

## Primary scripts

| File | Type | Purpose |
|---|---|---|
| `ORB_ICT_Manual_Signals_v3.pine` | Indicator | Confirmed-bar ORB signals, M5/M15/M30 Signal Flow, configurable ORB presentation and manual entry/SL/TP estimates. |
| `ORB_ICT_Backtest_Strategy_v2.pine` | Strategy | Separate Strategy Tester implementation retained for controlled historical comparisons. |
| `SMC_Context_Companion_v1.pine` | Indicator | HTF pullback-continuation and sweep-reversal models with session context, OB/FVG proxies and filtered BUY/SELL plans. |
| `ORB_ICT_Session_Liquidity_Framework_v2.pine` | Indicator | Clean session and ORB observation framework with compact visuals and confirmed-bar lifecycle logic. |

The manual ORB indicator and backtest strategy are deliberately separate. Changes to one should not be assumed to exist in the other.

## Documentation

- [`ORB_V3_SETUP_GUIDE.md`](ORB_V3_SETUP_GUIDE.md) — ORB v3 installation, signal rules, dashboard and risk-estimate notes.
- [`SMC_CONTEXT_GUIDE.md`](SMC_CONTEXT_GUIDE.md) — SMC definitions, signal filters, risk versus confirmation entries and limitations.
- [`ORB_ICT_BACKTEST_GUIDE.md`](ORB_ICT_BACKTEST_GUIDE.md) — Strategy Tester setup and comparison controls.
- [`ORB Research 2026-09-14/README.md`](ORB%20Research%202026-09-14/README.md) — export analysis, findings and caveats.
- `ORB_ICT_Session_Liquidity_Framework_Manual.docx` and `.pdf` — short user manual for the session framework.

## Validation

Generate or verify the standalone ORB manual source:

```bash
python3 tools/build_orb_v3.py --target manual
python3 tools/build_orb_v3.py --check --target manual
```

Run the local SMC rule-model and source-guard tests:

```bash
python3 -m unittest discover -s tools -p 'test_smc_context.py' -v
```

These checks verify source consistency and modeled rules. They are not a Pine compiler and do not prove profitability, robustness or live execution. Compile the exact Pine source in TradingView on the intended symbol, broker feed and standard-candle timeframe before relying on its display.

## Repository policy

- Raw Strategy Tester exports, paper-trading account exports, temporary renders and generated QA output remain local and are excluded from Git.
- The licensed third-party ICT reference script is excluded and must not be redistributed.
- The `market-dashboard` application is maintained in its own repository and is excluded here to avoid embedding one Git repository inside another.
- No script connects to a broker or places live orders.
- BUY/SELL labels, estimated levels and scores are analytical outputs—not probabilities, recommendations or guaranteed fills.

## Working conventions

1. Preserve confirmed-bar behavior and avoid future-data assumptions.
2. Record the symbol, feed, chart timeframe, date range, costs and all changed inputs for comparisons.
3. Keep indicator development separate from Strategy Tester changes unless both are explicitly requested.
4. Regenerate standalone Pine files after modifying their source fragments.
5. Recreate TradingView alerts after code or input changes because alerts retain a saved script snapshot.
