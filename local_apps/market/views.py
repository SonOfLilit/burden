from django.shortcuts import get_object_or_404, redirect, render
from django.http import HttpResponse

from design.models import ChoreType
from schedule.models import ScheduleRule
from market.models import Allocation


def update_allocations(request):
    """
    Generates allocations for `ChoreType` and commits them.
    """
    # TODO: update docs when adding handling of updating allocations

    # TODO: permissions (either check membership in chore owners
    # directly or check permission to edit schedule)

    chore = get_object_or_404(ChoreType, pk=request.POST["chore"])

    # TODO: Handle this case
    if chore.allocation_set.count() > 0:
        raise ValueError("Updating allocations not yet supported, only creating from scratch")

    allocation_plan = ScheduleRule.calculate_allocations(chore)

    for (date, days), quantity in allocation_plan.iteritems():
        assert quantity >= 0
        for _i in xrange(quantity):
            Allocation.objects.create(chore=chore, date=date, days=days)

    return redirect_back(request)


def redirect_back(request):
    """
    Redirects to previous page, if possible by referrer, else with
    javascript `history.go(-1)`.
    """
    if "HTTP_REFERRER" in request.META:
        return redirect(request.META["HTTP_REFERRER"])

    # TODO: More crowd-pleasing redirect_back.html
    return render(request, "market/redirect_back.html")
