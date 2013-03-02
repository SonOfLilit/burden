from django.db import transaction
from django.utils.translation import ugettext_lazy as _

from schedule.models import ScheduleRule
from market.models import Allocation


def update_allocations(modeladmin, request, chores):
    for chore in chores:
        try:
            update_chore_allocations(chore)
            modeladmin.message_user(request, _('Allocations for %s updated') % chore)
        except Exception as e:
            modeladmin.message_user(request, _('Allocation update for %s failed: %s') % (chore, e))

@transaction.commit_on_success
def update_chore_allocations(chore):
    # TODO: Handle this case
    if chore.allocation_set.count() > 0:
        raise ValueError("Updating allocations not yet supported, only creating from scratch")

    allocation_plan = ScheduleRule.calculate_allocations(chore)
    for (date, days), quantity in allocation_plan.iteritems():
        assert quantity >= 0
        for _i in xrange(quantity):
            Allocation.objects.create(chore=chore, date=date, days=days)
