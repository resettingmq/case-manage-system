from django.views import generic

from . import models, datatables

from utils.views import DataTablesListView, ConfiguredModelFormMixin,\
    RelatedEntityView, DisablementView, FormMessageMixin


class IncomeListView(DataTablesListView):
    dt_config = datatables.IncomeDataTable
    model = models.Income
    template_name = 'income/income_list.html'


class IncomeRelatedEntityView(RelatedEntityView):
    model = models.Income
    pk_url_kwarg = 'income_id'
    template_name = 'income/income_detail.html'


class IncomeCreateView(FormMessageMixin, ConfiguredModelFormMixin, generic.CreateView):
    model = models.Income
    template_name = 'income/income_create.html'


class IncomeDisableView(DisablementView):
    model = models.Income
    pk_url_kwarg = 'income_id'
