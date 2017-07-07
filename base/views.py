from django.shortcuts import render
from django.views import generic

from utils.views import DataTablesListView
from utils.utils import ModelDataTable, DataTablesColumn
from . import models

# Create your views here.


class ClientDataTable(ModelDataTable):
    name = DataTablesColumn()
    country__name_chs = DataTablesColumn()
    country__continent__name_chs = DataTablesColumn()

    dt_serverSide = True
    dt_processing = True

    class Meta:
        model = models.Client
        fields = ['is_agent']
        column_order = ['country__continent__name_chs', 'name', 'is_agent', 'country__name_chs']


def index(request):
    return render(request, 'base/index.html')


class ClientListView(DataTablesListView):
    dt_config = ClientDataTable
    model = models.Client
    template_name = 'base/client_list.html'
