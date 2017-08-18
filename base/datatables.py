# -*- coding: utf-8 -*-

from utils.utils import ModelDataTable

from . import models


class ClientDataTable(ModelDataTable):
    class Meta:
        model = models.Client
        fields = ['name', 'is_agent', 'email', 'country__name_chs']
        titles = {
            'country__name_chs': '国家名',
        }
        detail_url_format = '/client/{}'


class TrademarkDataTable(ModelDataTable):
    class Meta:
        model = models.Trademark
        fields = ['name', 'client__name']
        detail_url_format = '/trademark/{}'


class TrademarkNationDataTable(ModelDataTable):
    class Meta:
        model = models.TrademarkNation
        fields = ['app_no', 'app_date', 'register_no', 'register_date',
                  'trademark__name', 'trademark__client__name',
                  'country__name_chs', 'state']
        titles = {
            'country__name_chs': '国家名',
        }
        detail_url_format = '/trademark/nation/{}'
