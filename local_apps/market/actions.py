from django.db import transaction
from django.utils.translation import ugettext_lazy as _

from schedule.models import ScheduleRule
from market.models import Allocation


def update_allocations(modeladmin, request, chores):
    """
    Generates allocations for many `ChoreType`s, each on a separate
    transaction.
    """
    for chore in chores:
        try:
            update_chore_allocations(chore)
            modeladmin.message_user(request,
                                    _('Allocations for %s updated') % chore)
        except Exception as e:  # pylint: disable=W0703
            modeladmin.message_user(
                request, _('Allocation update for %s failed: %s') % (chore, e))


@transaction.commit_on_success
def update_chore_allocations(chore):
    """
    Generates allocations for a `ChoreType` and commits them.

    Transactional: either all succeed or all fail.
    """
    # TODO: Handle this case
    if chore.allocation_set.count() > 0:
        raise ValueError("Updating allocations not yet supported, only creating from scratch")

    allocation_plan = ScheduleRule.calculate_allocations(chore)
    for (date, days), quantity in allocation_plan.iteritems():
        assert quantity >= 0
        for _i in xrange(quantity):
            Allocation.objects.create(chore=chore, date=date, days=days)
