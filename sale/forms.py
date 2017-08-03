# -*- coding: utf-8 -*-

from decimal import Decimal

from django.forms import ModelForm
from django.core.exceptions import ValidationError

from . import models


class ReceivableModelForm(ModelForm):
    class Meta:
        model = models.Receivable
        fields = ['no', 'amount', 'currency', 'subcase',
                  'due_date', 'sent_date', 'sent', ]


class ReceiptsModelForm(ModelForm):
    class Meta:
        model = models.Receipts
        fields = ['amount', 'currency', 'exchange_rate', 'transfer_charge',
                  'received_date', 'receivable']

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
