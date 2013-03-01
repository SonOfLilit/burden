"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from django.utils import unittest
from django.test.client import Client
import datetime
import dateutil.rrule
from design.models import ChoreType
from schedule.models import ScheduleRule
from market.models import Allocation
import market.views


class RedirectBackTests(TestCase):

    def test_referrer(self):
        referrer = "http://somewhere.over.the.rainbow"

        class Mock(object): pass

        request = Mock()
        request.META = {"HTTP_REFERRER": referrer}

        response = market.views.redirect_back(request)

        self.assertEqual(302, response.status_code)
        self.assertEqual(referrer, response["Location"])


class UpdateAllocationsTests(TestCase):

    fixtures = ["design"]

    ALL_DAYS = dateutil.rrule.weekdays
    DATE = datetime.date(2001, 1, 1)

    def setUp(self):
        self.client = Client()
        self.chore = ChoreType.objects.get(name="Waste Time")

    def rule(self, **kwargs):
        # code copied from schedule tests, for so little code it seems
        # better than forcing the reader to switch all the time
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

    def test_first_time(self):
        self.rule()
        response = self.client.post("/market/update_allocations/", {"chore": self.chore.pk})
        self.assertEqual(200, response.status_code)
        self.assertEqual(1, self.chore.allocation_set.count())
        self.assertIn("market/redirect_back.html", (t.name for t in response.templates))

    def test_illegal_chore(self):
        response = self.client.post("/market/update_allocations/", {"chore": 12345})
        self.assertEqual(404, response.status_code)

    def test_no_rules(self):
        response = self.client.post("/market/update_allocations/", {"chore": self.chore.pk})
        self.assertEqual(200, response.status_code)
        self.assertEqual(0, self.chore.allocation_set.count())
