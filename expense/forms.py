# -*- coding: utf-8 -*-

from django import forms

from . import models
from base import models as base_models
from case import models as case_models


class ExpenseModelForm(forms.ModelForm):
    class Meta:
        model = models.Expense
        fields = ['amount', 'currency', 'exchange_rate',
                  'incurred_date', 'expense_type', 'subcase']
        widgets = {
            'incurred_date': forms.TextInput(attrs={
                'data-provide': 'datepicker',
                'data-date-format': 'yyyy-mm-dd',
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk and (self.instance.payment or self.instance.receipts):
            # 在编辑模式下，如果关联了payment或者receipts
            # 则不显示subcase field
            del self.fields['subcase']
        else:
            self.fields['subcase'].queryset = case_models.SubCase.enabled_objects

        self.fields['currency'].queryset = base_models.Currency.enabled_objects
        self.fields['expense_type'].queryset = models.ExpenseType.enabled_objects
