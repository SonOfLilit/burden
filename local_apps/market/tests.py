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
        self.other_chore = ChoreType.objects.get(name="Waste More Time")

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

    def post_update_allocations(self, chores=None):
        chores = chores or [self.chore.pk]
        return self.client.post("/market/update_allocations/", {"chores": chores})

    def test_first_time(self):
        self.rule()
        response = self.post_update_allocations()
        self.assertEqual(200, response.status_code)
        self.assertEqual(1, self.chore.allocation_set.count())
        self.assertIn("market/redirect_back.html", (t.name for t in response.templates))
        message, = (m.message for m in response.context["messages"])
        self.assertIn("updated", message)


    def test_illegal_chore(self):
        response = self.post_update_allocations(chores=[12345])
        message, = (m.message for m in response.context["messages"])
        self.assertIn("Errors in parameters:", message)

    def test_no_rules(self):
        response = self.post_update_allocations()
        self.assertEqual(200, response.status_code)
        self.assertEqual(0, self.chore.allocation_set.count())

    def test_multiple_chores(self):
        self.rule()
        self.rule(chore=self.other_chore)
        response = self.post_update_allocations(chores=[self.chore.pk, self.other_chore.pk])
        self.assertEqual(200, response.status_code)
        self.assertEqual(1, self.chore.allocation_set.count())
        self.assertEqual(1, self.other_chore.allocation_set.count())


# warning: complicated tests ahead, read slowly and carefully
class UpdateAllocationsTransactionTest(TransactionTestCase):

    fixtures = ["design"]

    DATE = datetime.date(2001, 1, 1)

    def setUp(self):
        self.client = Client()
        self.chore = ChoreType.objects.get(name="Waste Time")
        self.other_chore = ChoreType.objects.get(name="Waste More Time")

    @mock.patch("schedule.models.ScheduleRule.calculate_allocations")
    def test_nothing_commited_on_error(self, calculate_allocations):
        # first, we mock calculate_allocations() to return a sequence
        # that will have a legal value and then an illegal one
        mock_dict, legal, illegal = self.mock_dict([((self.DATE, 3), 1), ((self.DATE, 3), -1)])
        calculate_allocations.return_value = mock_dict

        # since this test is implementation-based, lets make sure the
        # implementation acts as we assume: iterates over the results
        # of calculate_allocations and asserts that the quantities are
        # non-negative before creating `Allocation`s

        # we call the view, it should have a legal `chore` parameter,
        # doesn't matter which since our mocked
        # `calculate_allocations` ignores it. It should fail the
        # assertion when it reaches `illegal_allocations`
        self.client.post("/market/update_allocations/", {"chores": [self.chore.pk]})

        # to know it reached `legal` /before/ failing the assertion on
        # `illegal_allocations`, lets make sure they were unpacked
        legal.__iter__.assert_called_with()
        illegal.__iter__.assert_called_with()

        # OK, now lets do the actual test: make sure nothing was commited
        self.assertEqual(0, self.chore.allocation_set.count())

    @mock.patch("schedule.models.ScheduleRule.calculate_allocations")
    def test_other_chores_unaffected_by_error(self, calculate_allocations):
        mock_dict, _ = self.mock_dict([((self.DATE, 3), -1)])
        other_mock_dict, _ = self.mock_dict([((self.DATE, 3), 1)])
        calculate_allocations.side_effect = [mock_dict, other_mock_dict]
        response = self.client.post("/market/update_allocations/",
                                    {"chores": [self.chore.pk, self.other_chore.pk]})

        self.assertEqual(0, self.chore.allocation_set.count())
        self.assertEqual(1, self.other_chore.allocation_set.count())
        failure_message, success_message = (m.message for m in response.context["messages"])
        self.assertIn("failed", failure_message)
        self.assertIn("updated", success_message)


    def mock_dict(self, pairs):
        """
        Helps with mocking `calculate_allocations()`'s return value.

        Returns an object that behaves like a `dict` would to
        `iteritem()` but yields the given pairs in the given
        order. The pairs are also mocked and returned so that it can
        be asserted that they were actually accessed.

        Returns a sequence with first item being mock dict and rest of
        items being mocked pairs in order received.

        Example:

            >> mock_dict, legal, illegal = self.mock_dict([((self.DATE, 3), 1), ((self.DATE, 3), -1)])
            >> calculate_allocations.return_value = mock_dict
            >> self.client.post("/market/update_allocations/", {"chores": [self.chore.pk]})
            >> legal.__iter__.assert_called_with()
            >> illegal.__iter__.assert_called_with()
        """
        mock_pairs = []
        for pair in pairs:
            mock_pair = mock.MagicMock()
            mock_pair.__iter__.return_value = iter(pair)
            mock_pairs.append(mock_pair)

        mock_dict = mock.Mock()
        mock_dict.iteritems = mock.Mock(return_value=mock_pairs)

        return ([mock_dict] + mock_pairs)
