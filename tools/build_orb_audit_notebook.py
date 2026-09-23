"""Create the compact, rerunnable reader-facing audit notebook with nbformat."""
from pathlib import Path
import nbformat as nbf

ROOT=Path(__file__).resolve().parents[1]
cells=[]
def md(text):cells.append(nbf.v4.new_markdown_cell(text))
def code(text):cells.append(nbf.v4.new_code_cell(text))
md('''# ORB export audit — 14 September 2026

## tl;dr

44 workbooks represent 41 distinct runs, not 44 independent confirmations. The old results suggest research candidates, not a proven winner. Paper trading has 10 closed trades, 5 winners, and +ZAR 4,890.11 reconciled to the balance ledger. The new Pine filters and 90-minute delay must be tested prospectively.

This notebook reproduces evidence for `README.md`; it does not execute Pine or run a new price-series backtest.''')
md('''## Context & Methods

### Key Assumptions

- Export display timestamps are Africa/Johannesburg (UTC+2), confirmed by the user; session calculations use each workbook's input timezone.
- A trade's PnL is duplicated on entry and exit rows: group by trade number and count the closed exit once. Exclude `Open` exit placeholders from closed performance.
- Budget-normalized result = net PnL / (reconstructed pre-entry equity × risk percentage). This is not exact trade R or a rerun at lower risk.
- Comparisons use within-pair overlapping history. Carried-in trades are excluded. The retrospective 70/30 split is not an untouched out-of-sample test.
- PF is undefined when there is no gross loss, not zero or a guaranteed infinite edge. Binomial intervals do not account for correlated trades or parameter-selection bias.

Dependencies: Python 3, openpyxl, pandas, nbformat and a Jupyter Python kernel. Source files remain read-only. Outputs are regenerated from the analysis script in `tools/`.''')
md('''## Data

### 1. Locate inputs and regenerate evidence

Run from this notebook directory or the Trading Board workspace. The subprocess uses the same Python interpreter as the notebook kernel.''')
code('''from pathlib import Path
import sys, subprocess, json
import pandas as pd
root = Path.cwd()
if not (root / "tools/analyze_orb_results.py").exists():
    root = root.parent
assert (root / "Strategy Tester Results").is_dir(), "Run from the Trading Board workspace or research folder"
result = subprocess.run([sys.executable, str(root / "tools/analyze_orb_results.py")], capture_output=True, text=True, check=True)
evidence = json.loads((root / "ORB Research 2026-09-14/analysis_evidence.json").read_text())
print(f"Read {len(evidence['runs'])} workbooks; {evidence['unique_runs']} distinct runs. Export timezone: {evidence['export_timezone']}.")''')
md('''### 2. Reconcile grain, source hashes and paper balance

The supplementary checks include source parity, risk formulas, range coverage examples and export reconciliation. They are not a local Pine interpreter.''')
code('''check = subprocess.run([sys.executable, str(root / "tools/test_orb_research.py")], capture_output=True, text=True, check=True)
print(check.stderr[-300:])
assert all(not run["issues"] for run in evidence["runs"])
paper = evidence["paper"]
assert abs(paper["reconciliation"]) < 0.001
pd.DataFrame([{"workbooks":len(evidence["runs"]), "unique_runs":evidence["unique_runs"], "open_positions_excluded":sum(len(r["open_trades"]) for r in evidence["runs"]), "paper_closed_trades":paper["closed_trades"]["n"], "paper_balance_ZAR":paper["balance_last"], "paper_net_ZAR":paper["closed_trades"]["net"]}])''')
md('''## Results

### 3. Review the candidate runs

These are old v1 results at 10% risk and 2.75R with placeholder costs. Different history lengths and session exits prevent an unqualified full-period ranking. Candidate rows are chosen for follow-up, not independently validated.''')
code('''comparison = pd.read_csv(root / "ORB Research 2026-09-14/run_comparison.csv")
candidate = ((comparison.pair.eq("XAUUSD") & comparison.direction.eq("Short only") & comparison.timeframe.eq("15 minutes")) | (comparison.pair.eq("EURUSD") & comparison.direction.eq("Long only") & comparison.timeframe.eq("5 minutes")) | (comparison.pair.eq("GBPJPY") & comparison.direction.eq("Short only") & comparison.timeframe.eq("5 minutes")) | (comparison.pair.eq("GBPUSD") & comparison.direction.eq("Both") & comparison.timeframe.eq("5 minutes") & comparison.model.eq("Break + retest")))
duplicate_files = {r["file"] for r in evidence["runs"] if r["duplicate_of"]}
comparison.loc[candidate & ~comparison.file.isin(duplicate_files), ["pair","symbol","timeframe","direction","model","trades","win_pct","pf","dd_pct","common_trades","common_pf"]].round(3)''')
md('''### 4. Compare early and later entries without claiming causality

Filtering existing trades cannot simulate setups the old strategy did not take. Here PF is computed from budget-normalized PnL.''')
code('''timing=[]
for run in evidence["runs"]:
    if run["duplicate_of"]: continue
    selected = (run["pair"] == "XAUUSD" and run["props"]["Timeframe"] == "15 minutes" and run["props"]["Trade direction"] == "Short only") or (run["pair"] == "GBPJPY" and run["props"]["Timeframe"] == "5 minutes" and run["props"]["Entry model"] == "Break + retest")
    if selected:
        for subset,summary in run["timing_diagnostic"].items():
            timing.append({"pair":run["pair"],"subset":subset,"closed_trades":summary["n"],"budget_PF":summary["pf"]})
pd.DataFrame(timing).round(3)''')
md('''### 5. Paper-trade uncertainty

Consolidated closed trades, not partial-close events. No original planned risk/setup labels are assumed.''')
code('''s=paper["closed_trades"]
pd.DataFrame([{"closed_trades":s["n"],"wins":s["wins"],"net_ZAR":s["net"],"PF":s["pf"],"win_pct":s["win_pct"],"Wilson_95_low_pct":s["ci_low"],"Wilson_95_high_pct":s["ci_high"],"net_without_best_ZAR":s["net_without_best"]}]).round(3)''')
md('''## Takeaways

- Prioritize EURUSD M5 London, GBPJPY M5 London, GBPUSD M5 London retest, and XAUUSD M15 NY short as hypotheses. Test both-direction controls.
- Do not universally impose a 90-minute delay: the XAUUSD and GBPJPY subsets point in different directions.
- Keep feed/dates/costs/stop/target/risk constant, freeze settings before an untouched period, and record all forward signals, including skips.
- A week is a usability review, not statistical validation. See `README.md` and `../ORB_V3_SETUP_GUIDE.md` for definitions, caveats, implementation and upload instructions.

Platform sources: [Strategy Tester execution](https://www.tradingview.com/pine-script-docs/concepts/strategies/), [timezones](https://www.tradingview.com/pine-script-docs/concepts/time/).''')
nb=nbf.v4.new_notebook(cells=cells,metadata={"kernelspec":{"display_name":"Python 3","language":"python","name":"python3"}})
nbf.validate(nb)
path=ROOT/'ORB Research 2026-09-14/ORB_export_audit.ipynb'
nbf.write(nb,path)
print(path)
