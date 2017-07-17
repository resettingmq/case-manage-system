from django.shortcuts import render

from utils.utils import ModelDataTable, DataTablesColumn

from . import models

# Create your views here.


class CaseDataTable(ModelDataTable):
    class Meta:
        model = models.Case
        fields = ['name', 'client__name', 'archive_no']
        detail_url_format = '/case/{}'
