from django.test import TestCase, TransactionTestCase
import mock

import datetime
import dateutil.rrule
from design.models import ChoreType
from schedule.models import ScheduleRule
import market.actions


class UpdateAllocationsTests(TestCase):

    fixtures = ["design"]

    ALL_DAYS = dateutil.rrule.weekdays
    DATE = datetime.date(2001, 1, 1)

    def setUp(self):
        self.chore = ChoreType.objects.get(name="Waste Time")
        self.other_chore = ChoreType.objects.get(name="Waste More Time")
        self.modeladmin = mock.Mock()

    def test_first_time(self):
        self.rule()
        self.update_allocations()
        self.assert_only_message("updated")
        self.assertEqual(1, self.chore.allocation_set.count())

    def test_no_rules(self):
        self.update_allocations()
        self.assert_only_message("updated")
        self.assertEqual(0, self.chore.allocation_set.count())

    def test_multiple_chores(self):
        self.rule()
        self.rule(chore=self.other_chore)
        self.update_allocations(chores=[self.chore, self.other_chore])
        self.assert_messages(["updated", "updated"])
        self.assertEqual(1, self.chore.allocation_set.count())
        self.assertEqual(1, self.other_chore.allocation_set.count())

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

    def update_allocations(self, chores=None):
        chores = chores or ChoreType.objects.filter(pk=self.chore.pk)
        request = mock.Mock()
        market.actions.update_allocations(self.modeladmin, request, chores)

    def assert_only_message(self, text):
        self.assert_messages([text])

    def assert_messages(self, expected):
        messages = []
        calls = self.modeladmin.message_user.mock_calls
        for _a, (_mock, message), _dict in calls:
            messages.append(message)
        self.assertEqual(len(expected), len(messages))
        for text, message in zip(expected, messages):
            self.assertIn(text, message)


# warning: complicated tests ahead, read slowly and carefully
class UpdateAllocationsTransactionTest(TransactionTestCase):

    # the only reason this is not the same class is that we can't
    # inherit TestCase, so lets do something ugly to get the
    # attributes we want here too. __dict__ is because of
    # unbound/bound method magic.
    fixtures = UpdateAllocationsTests.__dict__["fixtures"]
    DATE = UpdateAllocationsTests.__dict__["DATE"]
    setUp = UpdateAllocationsTests.__dict__["setUp"]
    update_allocations = UpdateAllocationsTests.__dict__["update_allocations"]
    assert_messages = UpdateAllocationsTests.__dict__["assert_messages"]
    # pylint: disable=E1101

    @mock.patch("schedule.models.ScheduleRule.calculate_allocations")
    def test_nothing_commited_on_error(self, calculate_allocations):
        # first, we mock calculate_allocations() to return a sequence
        # that will have a legal value and then an illegal one
        mock_allocation_plan, legal, illegal = self.mock_allocation_plan(
            [((self.DATE, 3), 1), ((self.DATE, 3), -1)])
        calculate_allocations.return_value = mock_allocation_plan

        # since this test is implementation-based, lets make sure the
        # implementation acts as we assume: iterates over the results
        # of calculate_allocations and asserts that the quantities are
        # non-negative before creating `Allocation`s

        # we call the view, it should have a legal `chore` parameter,
        # doesn't matter which since our mocked
        # `calculate_allocations` ignores it. It should fail the
        # assertion when it reaches `illegal_allocations`
        self.update_allocations()

        # to know it reached `legal` /before/ failing the assertion on
        # `illegal_allocations`, lets make sure they were unpacked
        legal.__iter__.assert_called_with()
        illegal.__iter__.assert_called_with()

        # OK, now lets do the actual test: make sure nothing was commited
        self.assertEqual(0, self.chore.allocation_set.count())
        self.assert_messages(["failed"])

    @mock.patch("schedule.models.ScheduleRule.calculate_allocations")
    def test_other_chores_unaffected_by_error(self, calculate_allocations):
        mock_plan, _ = self.mock_allocation_plan([((self.DATE, 3), -1)])
        other_mock_plan, _ = self.mock_allocation_plan([((self.DATE, 3), 1)])
        calculate_allocations.side_effect = [mock_plan, other_mock_plan]
        self.update_allocations(chores=[self.chore, self.other_chore])

        self.assertEqual(0, self.chore.allocation_set.count())
        self.assertEqual(1, self.other_chore.allocation_set.count())
        self.assert_messages(["failed", "updated"])

    def mock_allocation_plan(self, pairs):
        """
        Helps with mocking `calculate_allocations()`'s return value.

        Returns an object that behaves like a `dict` would to
        `iteritem()` but yields the given pairs in the given
        order. The pairs are also mocked and returned so that it can
        be asserted that they were actually accessed.

        Returns a sequence with first item being mock dict and rest of
        items being mocked pairs in order received.

        Example:
            >> mock_plan, legal, illegal = self.mock_allocation_plan(
            .. [((self.DATE, 3), 1), ((self.DATE, 3), -1)])
            >> calculate_allocations.return_value = mock_plan
            >> self.update_allocations()
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

    # pylint: enable=E1101
