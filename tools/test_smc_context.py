"""Source guards + independent rule-model fixtures; NOT a Pine interpreter/compiler.

Run: python3 -m unittest discover -s tools -p test_smc_context.py -v
Fixtures clarify intended semantics. TradingView compilation/replay is still needed.
"""
from dataclasses import dataclass
from pathlib import Path
import hashlib
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
SOURCE = (ROOT / "SMC_Context_Companion_v1.pine").read_text()


@dataclass
class Structure:
    high: float | None = None
    low: float | None = None
    direction: int = 0
    high_used: bool = False
    low_used: bool = False
    high_swept: bool = False
    low_swept: bool = False

    def step(self, high, low, close, pivot_high=None, pivot_low=None, confirmed=True):
        if not confirmed:
            return 0, False, False, False
        hs = self.high is not None and not self.high_used and not self.high_swept and high > self.high + .1 and close < self.high
        ls = self.low is not None and not self.low_used and not self.low_swept and low < self.low - .1 and close > self.low
        self.high_swept |= hs
        self.low_swept |= ls
        direction = 1 if self.high is not None and not self.high_used and close > self.high + .1 else -1 if self.low is not None and not self.low_used and close < self.low - .1 else 0
        shift = direction != 0 and self.direction != 0 and direction != self.direction
        if direction:
            self.direction = direction
            if direction == 1:
                self.high_used = True
            else:
                self.low_used = True
        # New confirmed pivots become available only after evaluating old levels.
        if pivot_high is not None:
            self.high = pivot_high
            self.high_used = self.high_swept = False
        if pivot_low is not None:
            self.low = pivot_low
            self.low_used = self.low_swept = False
        return direction, shift, hs, ls


def zone_result(direction, top, bottom, op, high, low, close, mode, expired=False):
    overlap = high >= bottom and low <= top
    invalid = close < bottom if direction == 1 else close > top
    far = low <= bottom if direction == 1 else high >= top
    rejection = overlap and (close > top and close > op if direction == 1 else close < bottom and close < op)
    remove = expired or invalid or (mode == "Wick reaches far edge" and far) or (mode == "First touch" and overlap)
    event = rejection and not expired and not invalid and not (mode == "Wick reaches far edge" and far)
    return remove, event


def candidate_slot_result(existing_slots, maximum, invalidated=False, replacement=False):
    """Independent model of the per-window candidate-slot rule."""
    used = existing_slots + 1
    if invalidated and replacement:
        used = max(0, used - 1)
    return used, used < maximum


class Rules(unittest.TestCase):
    def test_default_candidate_consumes_only_slot(self):
        self.assertEqual(candidate_slot_result(0, 1), (1, False))

    def test_invalid_candidate_can_return_slot_when_enabled(self):
        self.assertEqual(candidate_slot_result(0, 1, invalidated=True, replacement=True), (0, True))

    def test_multiple_slots_remain_sequentially_available(self):
        self.assertEqual(candidate_slot_result(0, 3), (1, True))
        self.assertEqual(candidate_slot_result(1, 3), (2, True))
        self.assertEqual(candidate_slot_result(2, 3), (3, False))

    def test_initial_break_is_not_choch(self):
        s = Structure(100, 90)
        self.assertEqual(s.step(102, 98, 101)[:2], (1, False))

    def test_close_break_consumed_once(self):
        s = Structure(100, 90)
        s.step(102, 98, 101)
        self.assertEqual(s.step(103, 99, 102)[0], 0)

    def test_opposite_break_is_shift(self):
        s = Structure(100, 90)
        s.step(102, 98, 101)
        self.assertEqual(s.step(95, 88, 89)[:2], (-1, True))

    def test_same_direction_new_swing_is_bos(self):
        s = Structure(100, 90)
        s.step(102, 98, 101)
        s.step(104, 98, 99, pivot_high=104)
        self.assertEqual(s.step(106, 102, 105)[:2], (1, False))

    def test_wick_sweep_is_not_close_break(self):
        s = Structure(100, 90)
        self.assertEqual(s.step(102, 95, 99), (0, False, True, False))
        self.assertFalse(s.step(103, 94, 98)[2])

    def test_low_sweep_is_symmetric(self):
        self.assertEqual(Structure(100, 90).step(95, 88, 91), (0, False, False, True))

    def test_both_sides_can_sweep_no_invented_direction(self):
        self.assertEqual(Structure(100, 90).step(102, 88, 95), (0, False, True, True))

    def test_no_unconfirmed_events(self):
        s = Structure(100, 90)
        self.assertEqual(s.step(102, 98, 101, confirmed=False), (0, False, False, False))
        self.assertEqual(s.direction, 0)
        self.assertFalse(s.high_used)

    def test_no_same_bar_new_pivot_break(self):
        s = Structure()
        self.assertEqual(s.step(102, 95, 101, pivot_high=100)[0], 0)
        self.assertEqual(s.step(103, 99, 102)[0], 1)

    def test_no_same_bar_new_pivot_sweep(self):
        s = Structure()
        self.assertFalse(s.step(102, 95, 99, pivot_high=100)[2])
        self.assertTrue(s.step(102, 95, 99)[2])

    def test_close_mitigation_survives_wick(self):
        self.assertEqual(zone_result(1, 100, 98, 99, 102, 97, 101, "Close through far edge"), (False, True))

    def test_wick_mitigation_suppresses_reaction(self):
        self.assertEqual(zone_result(1, 100, 98, 99, 102, 97, 101, "Wick reaches far edge"), (True, False))

    def test_first_touch_can_reject_then_delete(self):
        self.assertEqual(zone_result(-1, 102, 100, 101, 101.5, 98, 99, "First touch"), (True, True))

    def test_invalidated_zone_cannot_react(self):
        self.assertEqual(zone_result(-1, 102, 100, 101, 104, 99, 103, "Close through far edge"), (True, False))

    def test_expired_zone_cannot_react(self):
        self.assertEqual(zone_result(-1, 102, 100, 101, 101.5, 98, 99, "First touch", True), (True, False))

    def test_three_observed_days_includes_today(self):
        # Friday/Monday/Tuesday are consecutive observed days, not calendar offsets.
        self.assertEqual([born for born in range(1, 7) if 6 - born < 3], [4, 5, 6])


class SourceGuards(unittest.TestCase):
    def test_separate_indicator_no_trading_dashboard_or_orb_dependency(self):
        self.assertIn('indicator("SMC Context Companion v1.3"', SOURCE)
        for token in ("strategy(", "strategy.entry", "strategy.exit", "table.new", "import ", "scale.none"):
            self.assertNotIn(token, SOURCE)

    def test_both_htf_values_are_closed(self):
        self.assertIn('[direction[1], sh[1], sl[1]]', SOURCE)
        self.assertEqual(SOURCE.count('request.security('), 3)
        self.assertIn('f_htfPoi(poiSpan, obLookback, displacement, bodyFraction, gapMinimum)', SOURCE)
        self.assertIn('gaps = barmerge.gaps_off, lookahead = barmerge.lookahead_off', SOURCE)
        self.assertIn('input.timeframe("60"', SOURCE)
        self.assertIn('input.timeframe("240"', SOURCE)
        self.assertIn('timeframe.in_seconds() >= math.min', SOURCE)

    def test_formation_cannot_mitigate_own_zone(self):
        lifecycle = SOURCE.index('// Existing zone lifecycle first.')
        create = SOURCE.index('f_addZone(top, bottom, breakDir, "OB", dayNumber)')
        self.assertLess(lifecycle, create)
        self.assertIn('bar_index > z.born', SOURCE)

    def test_no_historical_signal_backdating(self):
        self.assertIn('label.new(bar_index, level, caption', SOURCE)
        self.assertIn('box.new(bar_index, top, bar_index + projection', SOURCE)
        self.assertNotIn('label.new(bar_index - pivotLength', SOURCE)
        self.assertNotIn('offset = -', SOURCE)

    def test_pivots_admitted_after_structure_tests(self):
        self.assertLess(SOURCE.index('int breakDir = highLive'), SOURCE.index('if not na(pivotHigh)'))

    def test_object_limits_are_bounded(self):
        self.assertIn('while array.size(events) > eventLimit', SOURCE)
        self.assertIn('dayNumber - e.day >= retainDays', SOURCE)
        self.assertIn('dayNumber - z.day >= retainDays', SOURCE)
        self.assertIn('if count >= zoneCount', SOURCE)
        self.assertIn('line.delete(upper)', SOURCE)
        self.assertIn('label.delete(context)', SOURCE)

    def test_filtered_signal_layer_is_bounded_and_configurable(self):
        for token in (
            'input.int(1, "Maximum setups per opening window", minval = 1, maxval = 3',
            'input.bool(false, "Allow replacement after candidate invalidation"',
            'input.string("Confirmation entry", "Entry model"',
            'input.bool(true, "Require HTF 1 order block or FVG interaction"',
            'input.bool(true, "Require displacement to leave an entry FVG"',
            'input.bool(true, "Accept engulfing confirmation candle"',
            'input.bool(true, "Accept rejection / pin confirmation candle"',
            'array.size(smcPlans) < 30',
            'alertcondition(smcBuySignal, "SMC qualified BUY"',
            'alertcondition(smcSellSignal, "SMC qualified SELL"',
        ):
            self.assertIn(token, SOURCE)
        self.assertIn('windowSetupCount += 1', SOURCE)
        self.assertIn('windowSetupCount < maxSetupsPerWindow', SOURCE)
        self.assertIn('windowSetupCount := math.max(0, windowSetupCount - 1)', SOURCE)
        self.assertNotIn('openingUsed', SOURCE)

    def test_backtest_orb_sources_untouched(self):
        expected = {
            "ORB_ICT_Backtest_Strategy_v2.pine": "859072317149ee9d63abf63c62a55aa73c8e9d00ccc84bab50d68811bc2b8115",
            "ORB_ICT_Backtest_Strategy_v1.pine": "e91e981035c430b8869eb6c46ba10febbe454cfee2be9734288bd2cbed0569e9",
        }
        for name, digest in expected.items():
            self.assertEqual(hashlib.sha256((ROOT / name).read_bytes()).hexdigest(), digest)

    def test_balanced_delimiters_not_a_compile_test(self):
        text = re.sub(r'"(?:\\.|[^"\\])*"|//[^\n]*', '', SOURCE)
        stack = []
        pairs = {')': '(', ']': '[', '}': '{'}
        for char in text:
            if char in '([{':
                stack.append(char)
            elif char in ')]}':
                self.assertTrue(stack)
                self.assertEqual(stack.pop(), pairs[char])
        self.assertEqual(stack, [])


if __name__ == "__main__":
    unittest.main()
