# -*- coding: utf-8 -*-

from decimal import Decimal

from django.forms import ModelForm, TextInput, DecimalField
from django.core.exceptions import ValidationError

from . import models
from base import models as base_models
from case import models as case_models
from expense import models as expense_models

from utils.formfield.forms import ModelFormFieldSupportMixin
from utils.formfield.fields import ModelFormField


class ReceivableModelForm(ModelForm):
    class Meta:
        model = models.Receivable
        fields = ['no', 'amount', 'currency', 'subcase',
                  'sent_date', 'due_date']
        widgets = {
            'due_date': TextInput(attrs={
                'data-provide': 'datepicker',
                'data-date-format': 'yyyy-mm-dd',
            }),
            'sent_date': TextInput(attrs={
                'data-provide': 'datepicker',
                'data-date-format': 'yyyy-mm-dd',
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['currency'].queryset = base_models.Currency.enabled_objects
        self.fields['subcase'].queryset = case_models.SubCase.enabled_objects


class TransferChargeModelForm(ModelForm):
    amount = DecimalField(
        max_digits=7,
        decimal_places=2,
        label='金额',
        initial=Decimal
    )

    class Meta:
        model = expense_models.Expense
        fields = ['amount']


class ReceiptsModelForm(ModelFormFieldSupportMixin, ModelForm):
    transfer_charge = ModelFormField(
        TransferChargeModelForm,
        title='转账手续费（人民币）',
        prefix='receipts',
        using_template=True
    )

    class Meta:
        model = models.Receipts
        fields = ['amount', 'currency', 'exchange_rate',
                  'received_date', 'receivable']
        widgets = {
            'received_date': TextInput(attrs={
                'data-provide': 'datepicker',
                'data-date-format': 'yyyy-mm-dd',
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['currency'].queryset = base_models.Currency.enabled_objects
        self.fields['receivable'].queryset = models.Receivable.enabled_objects

    def clean(self):
        """
        : 用于保证amount与关联Receivable的关系
        : 因为希望直接使用cleaned_data['receivable']，
        : 所以是在clean()中实现而不是在clean_amount()中
        : 带来一个影响就是抛出的ValidationError不能关联到特定field
        :return: None if no ValidationError
        """
        old_amount = self.instance.amount or Decimal()
        new_amount = self.cleaned_data['amount']
        limit = self.cleaned_data['receivable'].unsettled_amount
        if new_amount - old_amount > limit:
            raise ValidationError('收款金额不能大于待收款金额')

    def before_save_related(self):
        # 在存储related formfield之前
        # 1. 将transfer_charge formfield的发生日期设置为付款日期
        # 2. 将expense_type_id设置为100（汇款手续费）
        self['transfer_charge'].inner_form.instance.incurred_date = self.instance.received_date
        self['transfer_charge'].inner_form.instance.expense_type_id = 101
