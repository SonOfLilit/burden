from dateutil.rrule import rrule, weekday

from django.core import exceptions, validators
from django.db import models
from django import forms
from django.utils.translation import ugettext_lazy as _
from south.modelsinspector import add_introspection_rules


class DaysOfWeekField(models.Field):
    """
    A set of days of week (as `dateutil.rrule.weekday`s)
    """
    description = "A set of days of week"


    CHOICES = (
        (str(0b01000000), _('Sundays')),
        (str(0b00000001), _('Mondays')),
        (str(0b00000010), _('Tuesdays')),
        (str(0b00000100), _('Wednesdays')),
        (str(0b00001000), _('Thursdays')),
        (str(0b00010000), _('Fridays')),
        (str(0b00100000), _('Saturdays')),
        (str(0b01001111), _('Weekdays')),
        (str(0b01111111), _('All Days')),
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
        if value is None or value == "":
            return None

        if isinstance(value, basestring):
            value = int(value)
            # and then process as usual

        if isinstance(value, int):
            # value is a mask of days
            if not 0 <= value <= 0b01111111:
                raise ValueError(repr(value))
            days = set()
            for i in xrange(7):
                if value & (1 << i):
                    days.add(weekday(i))
        else:
            days = set(value)

        if any(not isinstance(x, weekday) for x in days):
            raise ValueError("Days should be weekday objects: " + repr(days))
        if len(set(day.weekday for day in days)) != len(days):
            raise ValueError("Duplicate days: " + repr(days))
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
            mask |= 1 << day.weekday
        return mask

    def validate(self, value, model_instance):
        """
        Validates value and throws ValidationError.
        """
        # we override this because the default tries to validate the
        # set() object against self.choices and fails

        if not self.editable:
            # Skip validation for non-editable fields.
            return

        if value is None and not self.null:
            raise exceptions.ValidationError(self.error_messages['null'])

        if not self.blank and value in validators.EMPTY_VALUES:
            raise exceptions.ValidationError(self.error_messages['blank'])

    def formfield(self, **kwargs):
        defaults = {
            "form_class": forms.ChoiceField,
            }
        defaults.update(kwargs)
        return super(DaysOfWeekField, self).formfield(**defaults)

add_introspection_rules([], ["^schedule\.fields\.DaysOfWeekField"])
