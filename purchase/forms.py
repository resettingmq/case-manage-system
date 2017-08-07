# -*- coding: utf-8 -*-

from decimal import Decimal

from django import forms
from django.core.exceptions import ValidationError

from . import models
from base import models as base_models
from case import models as case_models
from expense import models as expense_models

from utils.formfield.forms import ModelFormFieldSupportMixin
from utils.formfield.fields import ModelFormField


class PayableModelForm(forms.ModelForm):
    class Meta:
        model = models.Payable
        fields = ['no', 'amount', 'currency', 'subcase',
                  'received_date', 'due_date']
        widgets = {
            'due_date': forms.TextInput(attrs={
                'data-provide': 'datepicker',
                'data-date-format': 'yyyy-mm-dd',
            }),
            'received_date': forms.TextInput(attrs={
                'data-provide': 'datepicker',
                'data-date-format': 'yyyy-mm-dd',
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['currency'].queryset = base_models.Currency.enabled_objects
        self.fields['subcase'].queryset = case_models.SubCase.enabled_objects


class TransferChargeModelForm(forms.ModelForm):
    amount = forms.DecimalField(
        max_digits=7,
        decimal_places=2,
        label='金额',
        initial=Decimal
    )

    class Meta:
        model = expense_models.Expense
        fields = ['amount']

    def __init__(self, *args, **kwargs):
        # form被初始化时，如果instance为空，
        # 则将expense_type指向默认的100（汇款手续费）
        super().__init__(*args, **kwargs)
        if self.instance.pk is None:
            self.instance.expense_type_id = 100


class PaymentModelForm(ModelFormFieldSupportMixin, forms.ModelForm):
    transfer_charge = ModelFormField(
        TransferChargeModelForm,
        title='转账手续费（人民币）',
        prefix='payment',
        using_template=True
    )

    class Meta:
        model = models.Payment
        fields = ['amount', 'currency', 'exchange_rate',
                  'paid_date', 'payable']
        widgets = {
            'paid_date': forms.TextInput(attrs={
                'data-provide': 'datepicker',
                'data-date-format': 'yyyy-mm-dd',
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['currency'].queryset = base_models.Currency.enabled_objects
        self.fields['payable'].queryset = models.Payable.enabled_objects

    def clean(self):
        """
        : 用于保证amount与关联Payable的关系
        : 因为希望直接使用cleaned_data['payable']，
        : 所以是在clean()中实现而不是在clean_amount()中
        : 带来一个影响就是抛出的ValidationError不能关联到特定field
        :return: None if no ValidationError
        """
        old_amount = self.instance.amount or Decimal()
        new_amount = self.cleaned_data['amount']
        limit = self.cleaned_data['payable'].unsettled_amount
        if new_amount - old_amount > limit:
            raise ValidationError('付款金额不能大于待付款金额')
