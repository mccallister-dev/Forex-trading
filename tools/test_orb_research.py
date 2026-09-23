"""Supplementary data/formula/source checks. NOT a local Pine interpreter.
Actual compilation and chart execution must also be checked in TradingView.
"""
import json
import math
import unittest
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo
from hashlib import sha256
from analyze_orb_results import stats
from build_orb_v3 import CORE, DIGEST, ROOT

def coverage(start, duration, bars):
    """Reference calculation for the complete-window coverage requirement."""
    expected=start; total=0; complete=False
    for opened,closed in bars:
        if not start<=opened<start+duration: continue
        if opened==start: complete=True;expected=opened
        complete=complete and opened==expected and closed<=start+duration
        expected=closed;total+=closed-opened
    return complete and total==duration and expected==start+duration

def quantity(equity, entry, distance, point_value, fx, step, risk=1, leverage=500, margin=25, cost=0):
    risk_qty=max(equity,0)*risk/100/((distance+cost)*point_value*fx)
    cap_qty=max(equity,0)*leverage*margin/100/(entry*point_value*fx)
    return math.floor(min(risk_qty,cap_qty)/step)*step

class SourceTests(unittest.TestCase):
    def test_shared_engine(self):
        for name in ['ORB_ICT_Manual_Signals_v3.pine','ORB_ICT_Backtest_Strategy_v2.pine']:
            source=(ROOT/name).read_text()
            self.assertIn(CORE,source)
            self.assertIn('Shared engine SHA256: '+DIGEST,source)
    def test_manual_has_no_orders(self):
        source=(ROOT/'ORB_ICT_Manual_Signals_v3.pine').read_text()
        self.assertNotIn('strategy.',source)
        self.assertIn('bar_index > p.bornBar',source)
        self.assertIn('slHit and tpHit',source)
        self.assertIn('not p.active and daySequence',source)
    def test_tester_model(self):
        source=(ROOT/'ORB_ICT_Backtest_Strategy_v2.pine').read_text()
        self.assertIn('margin_long = 0.2, margin_short = 0.2',source)
        self.assertIn('process_orders_on_close = false',source)
        self.assertIn('loss = positionLossTicks, profit = positionProfitTicks',source)
        self.assertNotIn('strategy.close',source)
    def test_confirmation_and_invalidation_order(self):
        self.assertIn('[close[1], ta.ema(close, emaLength)[1]]',CORE)
        self.assertIn('bar_index > s.breakBar',CORE)
        self.assertIn('bar_index > s.pullBar',CORE)
        self.assertLess(CORE.index('bool invalid ='),CORE.index('if eligible and rangeOk'))
        self.assertIn('if not invalid',CORE)
        self.assertIn('not s.used',CORE)
        self.assertIn('not delayWholeSetup or time >= start + delayMinutes * 60000',CORE)
        self.assertIn('bool delayReady = time_close >= start + delayMinutes * 60000',CORE)
        self.assertIn('continuation and f_directionPass(d) and delayReady',CORE)
    def test_independent_entry_modes(self):
        self.assertIn('options = ["Close breakout", "Break + retest", "Break + retest + continuation"]',CORE)
        self.assertIn('"Context filter", options = ["Off", "Required"]',CORE)
        self.assertNotIn('entryModel == "ORB baseline"',CORE)
        self.assertIn('if candidate != 0 and delayReady and f_directionPass(candidate)',CORE)
        self.assertEqual(CORE.count('s.used := true'),1)
    def test_close_context_has_no_same_impulse_fib(self):
        start=CORE.index('if closeEntry\n')
        end=CORE.index('else if s.phase == 1',start)
        branch=CORE[start:end]
        self.assertIn('s.phase := 0',branch)
        self.assertIn('delayReady and (not requireContext',branch)
        self.assertNotIn('fibTouch',branch)
        self.assertIn('useFib and not closeEntry',CORE)
    def test_originals_unchanged(self):
        expected={'ORB_ICT_Backtest_Strategy_v1.pine':'e91e981035c430b8869eb6c46ba10febbe454cfee2be9734288bd2cbed0569e9','ORB_ICT_Session_Liquidity_Framework_v2.pine':'dba6305a2de4a367b898d57ee46ab6b78bec56485c17657487da2ec32f912032'}
        for name,digest in expected.items():self.assertEqual(sha256((ROOT/name).read_bytes()).hexdigest(),digest)

class FormulaTests(unittest.TestCase):
    def test_complete_range(self):self.assertTrue(coverage(0,30,[(x,x+5) for x in range(0,30,5)]))
    def test_missing_first_bar(self):self.assertFalse(coverage(0,30,[(x,x+5) for x in range(5,30,5)]))
    def test_missing_middle_bar(self):self.assertFalse(coverage(0,30,[(0,5),(5,10),(15,20),(20,25),(25,30)]))
    def test_bar_crosses_end(self):self.assertFalse(coverage(0,30,[(0,20),(20,40)]))
    def test_delayed_range(self):self.assertTrue(coverage(90,30,[(90,105),(105,120)]))
    def test_risk_and_cost(self):
        self.assertEqual(quantity(10000,2500,10,1,18,0.01),0.55)
        self.assertLess(quantity(10000,2500,10,1,18,0.01,cost=2),0.55)
        self.assertEqual(quantity(0,2500,10,1,18,0.01),0)
    def test_exposure_cap(self):
        qty=quantity(10000,2500,.001,1,18,.01)
        self.assertLessEqual(qty*2500*18,10000*500*.25)
    def test_margin_and_compounding(self):
        self.assertEqual(100/500,.2)
        self.assertAlmostEqual((.9**10)*100,34.86784401)
        self.assertAlmostEqual((.99**10)*100,90.43820750088044)
    def test_ny_dst_in_sast(self):
        winter=datetime(2026,1,15,8,tzinfo=ZoneInfo('America/New_York'))
        summer=datetime(2026,7,15,8,tzinfo=ZoneInfo('America/New_York'))
        self.assertEqual(winter.astimezone(ZoneInfo('Africa/Johannesburg')).hour,15)
        self.assertEqual(summer.astimezone(ZoneInfo('Africa/Johannesburg')).hour,14)
    def test_break_even_and_pf(self):
        s=stats([{'pnl':x} for x in [3,-1,-1,-1]])
        self.assertEqual(s['net'],0);self.assertEqual(s['pf'],1);self.assertEqual(s['breakeven_pct'],25)

class EvidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.data=json.loads((ROOT/'ORB Research 2026-09-14/analysis_evidence.json').read_text())
    def test_grain_duplicates_and_reconciliation(self):
        self.assertEqual(len(self.data['runs']),44);self.assertEqual(self.data['unique_runs'],41)
        self.assertEqual(sum(bool(r['duplicate_of']) for r in self.data['runs']),3)
        for run in self.data['runs']:
            self.assertEqual(run['issues'],[])
            self.assertEqual(run['summary']['n'],run['summary']['reported_n'])
            self.assertEqual(len({t['number'] for t in run['trades']}),len(run['trades']))
    def test_open_positions_not_closed(self):
        self.assertEqual(sum(len(r['open_trades']) for r in self.data['runs']),5)
        for r in self.data['runs']:
            self.assertTrue(set(t['number'] for t in r['trades']).isdisjoint(t['number'] for t in r['open_trades']))
    def test_paper_balance(self):
        paper=self.data['paper'];self.assertEqual(paper['closed_trades']['n'],10)
        self.assertEqual(paper['closed_trades']['wins'],5)
        self.assertAlmostEqual(paper['balance_last']-paper['balance_first'],4890.1096230675)
        self.assertLess(abs(paper['reconciliation']),.001)
    def test_source_hashes(self):
        for run in self.data['runs']:self.assertEqual(sha256((ROOT/run['file']).read_bytes()).hexdigest(),run['sha256'])

if __name__=='__main__':unittest.main(verbosity=2)
