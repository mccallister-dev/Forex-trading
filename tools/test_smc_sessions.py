"""Independent session fixtures/source guards; not a Pine interpreter."""
import datetime as dt
from pathlib import Path
import unittest
from zoneinfo import ZoneInfo

SOURCE = (Path(__file__).resolve().parents[1] / 'SMC_Context_Companion_v1.pine').read_text()

def active(utc_time, zone, hour, minute, duration=60, bar_minutes=5):
    local = utc_time.astimezone(ZoneInfo(zone))
    start = local.replace(hour=hour, minute=minute, second=0, microsecond=0)
    if local < start:
        start -= dt.timedelta(days=1)
    end = start + dt.timedelta(minutes=duration)
    return start.weekday() < 5 and start <= local < end and local + dt.timedelta(minutes=bar_minutes) <= end

def trigger(side, close, level, bar, swept_bar, displaced, valid_zone=True):
    broken = bar > swept_bar and (close > level + .1 if side == 1 else close < level - .1)
    return broken, broken and displaced and valid_zone

class SessionRules(unittest.TestCase):
    def test_new_york_dst(self):
        for month, utc_hour in [(1, 13), (7, 12)]:
            self.assertTrue(active(dt.datetime(2026, month, 6, utc_hour, tzinfo=dt.timezone.utc), 'America/New_York', 8, 0))
            self.assertFalse(active(dt.datetime(2026, month, 6, utc_hour-1, tzinfo=dt.timezone.utc), 'America/New_York', 8, 0))

    def test_end_excluded_and_partial_bar_rejected(self):
        self.assertFalse(active(dt.datetime(2026, 9, 18, 8, 0, tzinfo=dt.timezone.utc), 'Europe/London', 8, 0))
        self.assertFalse(active(dt.datetime(2026, 9, 18, 7, 58, tzinfo=dt.timezone.utc), 'Europe/London', 8, 0))

    def test_weekend_and_overnight_opening_date(self):
        self.assertFalse(active(dt.datetime(2026, 9, 19, 7, 0, tzinfo=dt.timezone.utc), 'Europe/London', 8, 0))
        self.assertTrue(active(dt.datetime(2026, 9, 19, 0, 10, tzinfo=dt.timezone.utc), 'UTC', 23, 30, duration=120))

    def test_later_displaced_break_only(self):
        self.assertEqual(trigger(1, 102, 100, 4, 4, True), (False, False))
        self.assertEqual(trigger(1, 102, 100, 5, 4, True), (True, True))
        self.assertEqual(trigger(-1, 98, 100, 5, 4, True), (True, True))

    def test_weak_break_consumes_without_candidate(self):
        self.assertEqual(trigger(1, 102, 100, 5, 4, False), (True, False))
        self.assertEqual(trigger(1, 102, 100, 5, 4, True, False), (True, False))

    def test_pine_guards_and_independence(self):
        for rule in ['lowSweep != highSweep', 'bar_index > sweepBar', 'bar_index - j >= sweepBar', 'time_close < openingEnd', 'xloc = xloc.bar_time', 'not openingUsed', 'frozenTrigger := dir == 1 ? swingHigh : swingLow', 'time_close <= finish']:
            self.assertIn(rule, SOURCE)
        self.assertEqual(SOURCE.count('candidateBox := box.new('), 1)
        block = SOURCE[SOURCE.index('// Independent session candidate layer.'):SOURCE.index('// Admit pivots LAST:')]
        self.assertNotIn('showOb', block)
        self.assertNotIn('showFvg', block)
        self.assertIn('box.delete(candidateBox)', block)
        self.assertIn('openingUsed := true', block)

if __name__ == '__main__':
    unittest.main()
