from django.test import TestCase
import datetime
from schedule.models import ScheduleRule, ChoreType


class ScheduleTest(TestCase):
    fixtures = ["design"]

    def test_one_shot(self):
        date = datetime.date(2000, 1, 1)
        chore = ChoreType.objects.get(name="Waste Time")
        rule = ScheduleRule.objects.create(chore=chore, quantity=1, days=1, days_of_week=[1], start_date=date, end_date=date)

        # TODO: Move to manager
        allocations = ScheduleRule.allocations(ChoreType.objects.get(name="Waste Time"))
        self.assertEqual(1, len(allocations))
        self.assertEqual(date, allocations[0].date)
