from django.db import models
from django import forms
from django.utils.translation import ugettext_lazy as _
from south.modelsinspector import add_introspection_rules


class DaysOfWeekField(models.IntegerField):

    description = "A set of days of week (as numbers between 1 for Sunday and 7 for Saturday)"

    CHOICES = (
        (str(0b1000000), _('Sundays')),
        (str(0b0100000), _('Mondays')),
        (str(0b0010000), _('Tuesdays')),
        (str(0b0001000), _('Wednesdays')),
        (str(0b0000100), _('Thursdays')),
        (str(0b0000010), _('Fridays')),
        (str(0b0000001), _('Saturdays')),
        (str(0b1111100), _('Weekdays')),
        )

    __metaclass__ = models.SubfieldBase

    def __init__(self, *args, **kwargs):
        kwargs["choices"] = self.CHOICES
        super(DaysOfWeekField, self).__init__(self, *args, **kwargs)

    def to_python(self, value):
        """
        Converts value assigned or read from database into correct
        format: set of day numbers.
        """
        if isinstance(value, basestring):
            value = int(value)
        if isinstance(value, int):
            # value is a mask of days
            if not 0 <= value <= 0b01111111:
                raise ValueError(repr(value))
            days = set()
            for i in xrange(7):
                if value & (1 << i):
                    days.add(i + 1)
        else:
            days = set(value)

        if days and (min(days) < 1 or max(days) > 7):
            raise ValueError("Invalid days: " + repr(days))
        return days

    def get_prep_value(self, days):
        """
        Prepares a value for storage in DB.
        """
        # as seen in django core fields.
        # if we don't do this, during South migration we get here days being
        # repr(set()), not sure why as this seems opposed to documentation
        days = self.to_python(days)
        mask = 0
        for day in days:
            if not 1 <= day <= 7:
                raise ValueError(repr(day))
            mask |= 1 << (day - 1)
        return mask

    def formfield(self, **kwargs):
        defaults = {
            "form_class": forms.TypedChoiceField,
            "coerce": lambda s: self.get_prep_value(int(s, 2)),
            "empty": None
            }
        defaults.update(kwargs)
        return super(DaysOfWeekField, self).formfield(**defaults)

add_introspection_rules([], ["^schedule\.fields\.DaysOfWeekField"])
