from dateutil.rrule import *

from django.db import models
from django.utils.translation import ugettext_lazy as _

from design.models import ChoreType
from schedule.fields import DaysOfWeekField

class ScheduleRule(models.Model):
    """
    Represents schedules for chore allocations.

    Example schedules:

    * 3 * 1 day starting Mondays and Wednesdays between 1/1 and 1/3

    * 5 * 3 days starting Sundays between 1/1 and 31/12 (if 31/12 is
      Sunday, the 31/12-2/1 will be generated. If 1/1 is a Monday, the
      first allocation generated will be on the 6/1)

    * 2 * 14 days starting Sundays between 1/1 and 31/12 (in which
      case, since the chore is between 7 and 14 days long, allocations
      will only be generated in odd weeks, relative to the first week
      where chores are generated. Currently there is no support for
      chores longer than 14 days)
    """
    # NOTE: Having business logic that determines intervals based on
    # days is a bit awkward. Perhaps just have an interval field and
    # be done with it?

    chore = models.ForeignKey(ChoreType)
    quantity = models.IntegerField()
    days = models.IntegerField()
    days_of_week = DaysOfWeekField()
    start_date = models.DateField()
    end_date = models.DateField()
    # TODO: rules_revision = models.ForeignKey(ScheduleRulesRevision, blank=True)
    # TODO: test that only revisionless rules are used by calculate_allocations()
    # TODO: save_rules_revision(), make calculate_allocations() action call it
    # TODO: Prevent editing of rules with rules_revision


    class Meta:
        verbose_name = _('Schedule Rule')
        verbose_name_plural = _('Schedule Rules')

    def __unicode__(self):
        return u"%d X %d days of %s [%s - %s]" % (
            self.quantity, self.days, self.chore, self.start_date, self.end_date)

    # TODO: move to manager?
    @classmethod
    def calculate_allocations(cls, chore):
        """
        Generates a ChoreType's allocations.

        Returns a dict from (date, days) to quantity.

        TODO: Support "year" in which to generate allocations.
        """
        rules = ScheduleRule.objects.filter(chore=chore)
        # dictionary from (date, days) to quantity
        allocations = {}
        for rule in rules:

            # rrule() treats empty sequences as if they were not there
            # and uses the default which is all days of week. We can't
            # have that
            if len(rule.days_of_week) == 0:
                raise ValueError(_('Rules with no days of week not supported'))

            if 0 < rule.days <= 7:
                interval = 1
            elif 7 < rule.days <= 14:
                interval = 2
            else:
                raise ValueError(_('Allocations above 2 weeks not supported'))

            for date in rrule(WEEKLY, dtstart=rule.start_date, until=rule.end_date,
                              byweekday=rule.days_of_week, interval=interval):
                # datetime object to date object
                date = date.date()
                allocations[date, rule.days] = allocations.get((date, rule.days), 0) + rule.quantity

        for (date, days), quantity in allocations.iteritems():
            if quantity < 0:
                raise ValueError(_('Negative quantity of %(chore)s at %(date)s') % locals())
        return allocations
