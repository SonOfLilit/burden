from django import forms

from design.models import ChoreType


class UpdateAllocationsForm(forms.Form):
    chores = forms.ModelMultipleChoiceField(queryset=ChoreType.objects.all())
