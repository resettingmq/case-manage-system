# -*- coding: utf-8 -*-

from utils.utils import ModelDataTable

from . import models


class ReceivableDataTable(ModelDataTable):
    class Meta:
        model = models.Receivable
        fields = ['no', 'amount', 'unsettled_amount',
                  'currency__name_chs', 'subcase__name']
        detail_url_format = '/receivable/{}'


class ReceiptsDataTable(ModelDataTable):
    class Meta:
        model = models.Receipts
        fields = ['amount', 'currency__name_chs', 'exchange_rate',
                  'received_date', 'receivable__no']
        detail_url_format = '/receipts/{}'
