# -*- coding: utf-8 -*-

from django import forms

from . import models
from base import models as base_models
from case import models as case_models


class IncomeModelForm(forms.ModelForm):
    class Meta:
        model = models.Income
        fields = ['amount', 'currency', 'exchange_rate',
                  'incurred_date', 'income_type', 'subcase']
        widgets = {
            'incurred_date': forms.TextInput(attrs={
                'data-provide': 'datepicker',
                'data-date-format': 'yyyy-mm-dd',
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['currency'].queryset = base_models.Currency.enabled_objects
        self.fields['subcase'].queryset = case_models.SubCase.enabled_objects
