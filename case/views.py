from django.views import generic

from utils.utils import ModelDataTable, DataTablesColumn
from utils.views import DataTablesListView

from . import models

# Create your views here.


class CaseDataTable(ModelDataTable):
    class Meta:
        model = models.Case
        fields = ['name', 'client__name', 'archive_no']
        detail_url_format = '/case/{}'


class CaseListView(DataTablesListView):
    dt_config = CaseDataTable
    model = models.Case
    template_name = 'case/case_list.html'
