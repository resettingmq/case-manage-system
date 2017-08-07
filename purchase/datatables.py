# -*- coding: utf-8 -*-

from utils.utils import ModelDataTable

from . import models


class PayableDataTable(ModelDataTable):
    class Meta:
        model = models.Payable
        fields = ['no', 'amount', 'unsettled_amount', 'currency__name_chs',
                  'subcase__name', 'received_date', 'due_date', ]
        detail_url_format = '/payable/{}'


class PaymentDataTable(ModelDataTable):
    class Meta:
        model = models.Payment
        fields = ['amount', 'currency__name_chs', 'exchange_rate',
                  'paid_date', 'payable__no']
        detail_url_format = '/payment/{}'
