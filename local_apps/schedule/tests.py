from django.utils import unittest
from django.test import TestCase
import datetime
import dateutil.rrule
from dateutil.rrule import SU, TU
from dateutil.relativedelta import relativedelta
from schedule.models import ScheduleRule, ChoreType


class ScheduleTest(TestCase):
    fixtures = ["design"]

    ALL_DAYS = dateutil.rrule.weekdays
    DATE = datetime.date(2001, 1, 1)

    def setUp(self): 
        self.chore = ChoreType.objects.get(name="Waste Time")

    def rule(self, **kwargs):
        params = {
            "chore": self.chore,
            "quantity": 1,
            "days": 1,
            "days_of_week": self.ALL_DAYS,
            "start_date": self.DATE,
            "end_date": self.DATE
            }
        params.update(kwargs)
        return ScheduleRule.objects.create(**params)

    def test_one_shot(self):
        days = 6
        rule = self.rule(days=days)

        # TODO: Move to manager
        allocations = ScheduleRule.allocations(self.chore)
        self.assertEqual(1, len(allocations))
        self.assertEqual(self.chore, allocations[0].chore)
        self.assertEqual(self.DATE, allocations[0].date)
        self.assertEqual(days, allocations[0].days)

    def test_quantity(self):
        quantity = 3
        rule = self.rule(quantity=quantity)

        allocations = ScheduleRule.allocations(self.chore)
        self.assertEqual(quantity, len(allocations))
        for allocation in allocations:
            self.assertEqual(self.DATE, allocation.date)

    def test_date_range(self): 
        rule = self.rule(end_date=self.DATE + relativedelta(days=+1))
        allocations = ScheduleRule.allocations(self.chore)
        self.assertEqual(2, len(allocations))
        self.assertNotEqual(allocations[0].date, allocations[1].date)

    def test_big_date_range(self): 
        rule = self.rule(end_date=self.DATE + relativedelta(years=+1, days=-1))
        allocations = ScheduleRule.allocations(self.chore)
        self.assertEqual(365, len(allocations))

    def test_leap_year_date_range(self): 
        # 2000 was a leap year
        date = datetime.date(2000, 1, 1)
        rule = self.rule(start_date=date, end_date=date + relativedelta(years=+1, days=-1))
        allocations = ScheduleRule.allocations(self.chore)
        self.assertEqual(366, len(allocations))

    def test_days_of_week_none(self):
        rule = self.rule(days_of_week=[])
        try:
            allocations = ScheduleRule.allocations(self.chore)
            assert False
        except ValueError:
            pass

    def test_days_of_week_some(self):
        rule = self.rule(days_of_week=[SU, TU], end_date=self.DATE + relativedelta(weeks=+1, days=-1))
        allocations = ScheduleRule.allocations(self.chore)
        self.assertEqual(2, len(allocations))


    @unittest.skip("TODO")
    def test_multiple_rules(self):
        pass

    @unittest.skip("TODO")
    def test_negative_quantity(self):
        pass
