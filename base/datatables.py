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
        fields = ['trademark__name', 'country__name_chs',
                  'app_no', 'app_date', 'register_no', 'register_date',
                  'trademark__client__name', 'state']
        titles = {
            'country__name_chs': '进入国家',
        }
        detail_url_format = '/trademark/nation/{}'


class TrademarkNationNiceDataTable(ModelDataTable):
    class Meta:
        model = models.TrademarkNationNice
        fields = ['nice_class__name', 'goods']
        detail_url_format = '/trademark/nation/nice/{}'
        width = {
            'nice_class__name': '60px',
        }


class PatternDataTable(ModelDataTable):
    class Meta:
        model = models.Pattern
        fields = ['name', 'client__name']
        detail_url_format = '/pattern/{}'


class PatternNationDataTable(ModelDataTable):
    class Meta:
        model = models.PatternNation
        fields = ['pattern__name', 'country__name_chs',
                  'app_no', 'publication_no', 'publish_no', 'pattern_no',
                  'pattern__client__name', 'state']
        titles = {
            'country__name_chs': '进入国家',
        }
        detail_url_format = '/pattern/nation/{}'
