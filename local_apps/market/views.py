from django.shortcuts import redirect, render
from django.http import Http404
from django.db import transaction
from django.utils.translation import ugettext_lazy as _
from django.contrib import messages

from design.models import ChoreType
from schedule.models import ScheduleRule
from market.models import Allocation
from market.forms import UpdateAllocationsForm


def update_allocations(request):
    """
    Generates allocations for `ChoreType` and commits them.
    """
    # TODO: update docs when adding handling of updating allocations

    # TODO: permissions (either check membership in chore owners
    # directly or check permission to edit schedule)

    form = UpdateAllocationsForm(request.POST)
    if form.is_valid():

        chores = form.cleaned_data["chores"]

        for chore in chores:
            try:
                update_chore_allocations(chore)
                messages.success(request, _('Allocations for %s updated') % chore)
            except Exception, e:
                messages.error(request, _('Allocation update for %s failed: %s') % (chore, e))

    else:
        messages.error(request, _('Errors in parameters: %s') % form.errors)

    return redirect_back(request)

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


def redirect_back(request):
    """
    Redirects to previous page, if possible by referrer, else with
    javascript `history.go(-1)`.
    """
    if "HTTP_REFERRER" in request.META:
        return redirect(request.META["HTTP_REFERRER"])

    # TODO: More crowd-pleasing redirect_back.html
    return render(request, "market/redirect_back.html")
