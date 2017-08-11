# -*- coding: utf-8 -*-

from utils.utils import ModelDataTable

from . import models


class IncomeDataTable(ModelDataTable):
    class Meta:
        model = models.Income
        fields = ['amount', 'currency__name_chs', 'income_type__name',
                  'subcase__name']
        detail_url_format = '/income/{}'
