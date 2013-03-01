"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase, TransactionTestCase
from django.utils import unittest
from django.test.client import Client
import mock

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


# warning: complicated tests ahead, read slowly and carefully
class UpdateAllocationsTransactionTest(TransactionTestCase):

    fixtures = ["design"]

    DATE = datetime.date(2001, 1, 1)

    def setUp(self):
        self.client = Client()
        self.chore = ChoreType.objects.get(name="Waste Time")

    @mock.patch("schedule.models.ScheduleRule.calculate_allocations")
    def test_nothing_commited_on_error(self, calculate_allocations):
        # first, we mock calculate_allocations() to return a sequence
        # that will have a legal value and then an illegal one
        mock_legal_allocations = mock.MagicMock()
        mock_legal_allocations.__iter__.return_value = iter(((self.DATE, 3), 1))
        illegal_allocations = ((self.DATE, 3), -1)
        mock_dict = mock.Mock()
        mock_dict.iteritems = mock.Mock(
            return_value=[mock_legal_allocations, illegal_allocations])
        calculate_allocations.return_value = mock_dict

        # since this test is implementation-based, lets make sure the
        # implementation acts as we assume: iterates over the results
        # of calculate_allocations and asserts that the quantities are
        # non-negative before creating `Allocation`s

        # we call the view, it should have a legal `chore` parameter,
        # doesn't matter which since our mocked
        # `calculate_allocations` ignores it. It should fail the
        # assertion when it reaches `illegal_allocations`
        with self.assertRaises(AssertionError):
            response = self.client.post("/market/update_allocations/", {"chore": self.chore.pk})

        # to know it reached `mock_legal_allocations` before failing
        # the assertion on `illegal_allocations`, lets make sure it
        # was unpacked
        mock_legal_allocations.__iter__.assert_called_with()

        # OK, now lets do the actual test: make sure nothing was commited
        self.assertEqual(0, self.chore.allocation_set.count())
