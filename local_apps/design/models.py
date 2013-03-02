from django.db import models
from django.utils.translation import ugettext_lazy as _

from hr.models import Trait, Organization


class ChoreType(models.Model):
    """
    Represents a type of chore that needs to be done. There will be
    `Allocation`s of this chore at different dates and of different
    lengths, according to different `ScheduleRules`, and they will be
    assigned to be performed by their `owners` body, who will probably
    assign them to sub-bodies or `Worker`s, all of which might trade
    them with each other.
    """
    name = models.CharField(max_length=100)
    traits_required = models.ManyToManyField(
        Trait, related_name="chores_requiring_trait", blank=True)
    traits_forbidden = models.ManyToManyField(
        Trait, related_name="chores_forbidding_trait", blank=True)
    # Creator of `ChoreType` must be a manager in `owners`. `owners`
    # receives every allocation of this ChoreType and is responsible
    # for distributing it between its `Worker`s.
    # TODO: validate that creator of `ChoreType` is manager in `owners`
    owners = models.ForeignKey(Organization)

    class Meta:
        verbose_name = _('Chore Type')
        verbose_name_plural = _('Chore Types')

    def __unicode__(self):
        return self.name
