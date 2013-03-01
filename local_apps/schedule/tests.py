from django.utils import unittest
from django.test import TestCase
import datetime
import dateutil.rrule
from collections import namedtuple
from dateutil.rrule import SU, TU
from dateutil.relativedelta import relativedelta
from schedule.models import ScheduleRule, ChoreType


Alloc = namedtuple("Alloc", ["chore", "days", "date"])

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

    def get_allocations(self):
        raw_allocations = ScheduleRule.allocations(self.chore)
        allocations = []
        for (date, days), quantity in raw_allocations.iteritems():
            if quantity < 0:
                self.fail("negative quantity: " + str(quantity))
            for _i in xrange(quantity):
                allocations.append(Alloc(chore=self.chore, date=date, days=days))
        return allocations

    def test_one_allocation(self):
        days = 6
        self.rule(days=days)

        # TODO: Move to manager
        allocations = self.get_allocations()
        self.assertEqual(1, len(allocations))
        self.assertEqual(self.DATE, allocations[0].date)
        self.assertEqual(days, allocations[0].days)

    def test_quantity(self):
        quantity = 3
        self.rule(quantity=quantity)

        allocations = self.get_allocations()
        self.assertEqual(quantity, len(allocations))
        for allocation in allocations:
            self.assertEqual(self.DATE, allocation.date)

    def test_date_range(self): 
        self.rule(end_date=self.DATE + relativedelta(days=+1))
        allocations = self.get_allocations()
        self.assertEqual(2, len(allocations))
        self.assertNotEqual(allocations[0].date, allocations[1].date)

    def test_big_date_range(self): 
        self.rule(end_date=self.DATE + relativedelta(years=+1, days=-1))
        allocations = self.get_allocations()
        self.assertEqual(365, len(allocations))

    def test_leap_year_date_range(self): 
        # 2000 was a leap year
        date = datetime.date(2000, 1, 1)
        self.rule(start_date=date, end_date=date + relativedelta(years=+1, days=-1))
        allocations = self.get_allocations()
        self.assertEqual(366, len(allocations))

    def test_negative_date_range(self): 
        self.rule(end_date=self.DATE + relativedelta(days=-1))
        allocations = self.get_allocations()
        self.assertEqual(0, len(allocations))

    def test_days_of_week_none(self):
        self.rule(days_of_week=[])
        self.assertRaises(ValueError, self.get_allocations)

    def test_days_of_week_some(self):
        self.rule(days_of_week=[SU, TU], end_date=self.DATE + relativedelta(weeks=+1, days=-1))
        allocations = self.get_allocations()
        self.assertEqual(2, len(allocations))


    def test_biweekly_rule(self):
        self.rule(days=8, days_of_week=[TU], end_date=self.DATE + relativedelta(weeks=+4, days=-1))
        allocations = self.get_allocations()
        self.assertEqual(2, len(allocations))
        dates = sorted(x.date for x in allocations)
        # 2001 starts on a monday
        self.assertEqual([datetime.date(2001, 1, 2), datetime.date(2001, 1, 2 + 14)], dates)
        
    def test_triweekly_rule_not_supported(self):
        self.rule(days=15)
        self.assertRaises(ValueError, self.get_allocations)


    def test_multiple_rules(self):
        self.rule()
        self.rule()
        allocations = self.get_allocations()
        self.assertEqual(2, len(allocations))

    def test_negative_quantity(self):
        self.rule()
        self.rule(quantity=-1)
        allocations = self.get_allocations()
        self.assertEqual(0, len(allocations))

    def test_negative_quantity_rule_still_created(self):
        self.rule()
        self.rule()
        self.rule(quantity=-1)
        allocations = self.get_allocations()
        self.assertEqual(1, len(allocations))

    def test_negative_total_quantity(self):
        self.rule()
        self.rule(quantity=-2)
        self.assertRaises(ValueError, self.get_allocations)
