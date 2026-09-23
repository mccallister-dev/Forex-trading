"""Mechanically build the standalone manual and strategy Pine artifacts."""
from pathlib import Path
from hashlib import sha256
import argparse

ROOT=Path(__file__).resolve().parents[1]
HERE=Path(__file__).resolve().parent
HEADERS={
 'ORB_ICT_Manual_Signals_v3.pine':'indicator("ORB + ICT Manual Signals v3", shorttitle = "ORB Manual v3", overlay = true, max_lines_count = 450, max_labels_count = 150, max_bars_back = 600)',
 'ORB_ICT_Backtest_Strategy_v2.pine':'''strategy("ORB + ICT Backtest Strategy v2", shorttitle = "ORB Backtest v2", overlay = true,
    initial_capital = 10000, currency = "ZAR", pyramiding = 0,
    margin_long = 0.2, margin_short = 0.2,
    commission_type = strategy.commission.percent, commission_value = 0.0,
    slippage = 1, process_orders_on_close = false, calc_on_order_fills = false,
    calc_on_every_tick = false, max_bars_back = 600)'''}

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--check',action='store_true')
    parser.add_argument('--target',choices=['all','manual','strategy'],default='all')
    args=parser.parse_args()
    for name,header in HEADERS.items():
        is_manual='Manual' in name
        if args.target == 'manual' and not is_manual:
            continue
        if args.target == 'strategy' and is_manual:
            continue
        core_name='orb_v3_manual_core.pine.inc' if is_manual else 'orb_v3_core.pine.inc'
        core=(HERE/core_name).read_text()
        digest=sha256(core.encode()).hexdigest()
        tail='orb_v3_manual.pine.inc' if 'Manual' in name else 'orb_v2_strategy.pine.inc'
        result='//@version=6\n'+header+'\n// Shared engine SHA256: '+digest+'\n\n'+core+'\n'+(HERE/tail).read_text()
        path=ROOT/name
        if args.check:
            assert path.read_text()==result, f'{name}: stale generated file'
        else:
            path.write_text(result)
        print(name,sha256(result.encode()).hexdigest())

if __name__=='__main__':main()
