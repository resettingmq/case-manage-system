# -*- coding: utf-8 -*-

from utils.utils import ModelDataTable

from . import models


class SubCaseDataTable(ModelDataTable):
    class Meta:
        model = models.SubCase
        fields = ['name', 'settled', 'closed', 'agent__name', 'case__name', 'stage__name']
        detail_url_format = '/subcase/{}'
