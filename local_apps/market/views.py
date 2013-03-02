from django.shortcuts import redirect, render
from django.utils.translation import ugettext_lazy as _


def redirect_back(request):
    """
    Redirects to previous page, if possible by referrer, else with
    javascript `history.go(-1)`.
    """
    if "HTTP_REFERRER" in request.META:
        return redirect(request.META["HTTP_REFERRER"])

    # TODO: More crowd-pleasing redirect_back.html
    return render(request, "market/redirect_back.html")
