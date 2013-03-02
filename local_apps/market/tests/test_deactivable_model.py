from django.test import TestCase

import django.db.models
import datetime
from design.models import ChoreType
from hr.models import Worker, User
from market.models import Allocation, Assignment, Transaction


class DeactivableModelBase(object):

    fixtures = ["design"]

    MODEL = None

    def test_deleted_rows_only_in_full_queryset(self):
        a = self.create()
        b = self.create()
        b.delete()
        self.assert_equal_querysets([a], self.MODEL.objects.all())
        self.assert_equal_querysets([a, b],
                                    self.MODEL.objects.all_with_deleted())

    def test_cannot_edit(self):
        a = self.create()
        # pylint: disable=E1101
        with self.assertRaises(django.db.IntegrityError):
            a.save()

    def create(self):
        raise NotImplementedError()

    def assert_equal_querysets(self, a, b):
        idset = lambda s: set(x.id for x in s)
        a = idset(a)
        b = idset(b)
        self.assertEqual(a, b)  # pylint: disable=E1101


class AllocationDeactivableTest(DeactivableModelBase, TestCase):
    DATE = datetime.date(2001, 1, 1)

    MODEL = Allocation

    def setUp(self):
        self.chore = ChoreType.objects.get(name="Waste Time")

    def create(self):
        return Allocation.objects.create(chore=self.chore,
                                         date=self.DATE, days=3)


class AssignmentDeactivableTest(DeactivableModelBase, TestCase):
    DATE = datetime.date(2001, 1, 1)

    MODEL = Assignment

    def setUp(self):
        self.chore = ChoreType.objects.get(name="Waste Time")
        self.allocation = Allocation.objects.create(chore=self.chore,
                                                    date=self.DATE, days=3)
        self.user = User.objects.create(username="Avi")
        self.performer = Worker.objects.create(user=self.user)
        self.transaction = Transaction.objects.create()

    def create(self):
        return Assignment.objects.create(
            allocation=self.allocation,
            old_performer=self.performer,
            new_performer=self.performer,
            is_trade=False,
            transaction=self.transaction)


class TransactionDeactivableTest(DeactivableModelBase, TestCase):

    MODEL = Transaction

    def create(self):
        return Transaction.objects.create()
