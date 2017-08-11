# -*- coding: utf-8 -*-

from utils.utils import ModelDataTable

from . import models


class ClientDataTable(ModelDataTable):
    class Meta:
        model = models.Client
        fields = ['name', 'is_agent', 'country__name_chs']
        detail_url_format = '/client/{}'
