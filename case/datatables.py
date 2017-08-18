# -*- coding: utf-8 -*-

from utils.utils import ModelDataTable

from . import models


class CaseDataTable(ModelDataTable):
    class Meta:
        model = models.Case
        fields = ['name', 'client__name', 'archive_no', 'category__name']
        detail_url_format = '/case/{}'


class SubCaseDataTable(ModelDataTable):
    class Meta:
        model = models.SubCase
        fields = ['name', 'settled', 'closed', 'agent__name', 'case__name',
                  'category__name', 'stage__name']
        detail_url_format = '/subcase/{}'
