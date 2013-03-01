from django.utils.translation import ugettext_lazy as _
from django.contrib import admin
from design.models import ChoreType
from schedule.models import ScheduleRule


class ScheduleRuleInline(admin.TabularInline):
    model = ScheduleRule


class ChoreTypeAdmin(admin.ModelAdmin):
    list_display = ("name", "owners", "traits_required_string", "traits_forbidden_string")
    inlines = [ScheduleRuleInline]

    def traits_required_string(self, chore):
        return u", ".join([trait.name for trait in chore.traits_required.all()])
    traits_required_string.short_description = _('Traits Required')

    def traits_forbidden_string(self, chore):
        return ""
    traits_forbidden_string.short_description = _('Traits Forbidden')


admin.site.register(ChoreType, ChoreTypeAdmin)
