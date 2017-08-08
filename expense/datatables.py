# -*- coding: utf-8 -*-

from utils.utils import ModelDataTable

from . import models


class ExpenseDataTable(ModelDataTable):
    class Meta:
        model = models.Expense
        fields = ['amount', 'currency__name_chs', 'expense_type__name',
                  'subcase__name', 'payment', 'receipts']
        detail_url_format = '/expense/{}'
