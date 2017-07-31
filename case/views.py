from django.views import generic

from utils.utils import ModelDataTable, DataTablesColumn
from utils.views import DataTablesListView, ConfiguredModelFormMixin, RelatedEntityView

from . import models, forms

# Create your views here.


class CaseDataTable(ModelDataTable):
    class Meta:
        model = models.Case
        fields = ['name', 'client__name', 'archive_no', 'entry_country__name_chs',
                  'category__name']
        detail_url_format = '/case/{}'


class CaseListView(DataTablesListView):
    dt_config = CaseDataTable
    model = models.Case
    template_name = 'case/case_list.html'


class CaseRelatedEntityView(RelatedEntityView):
    model = models.Case
    form_class = forms.CaseModelForm
    pk_url_kwarg = 'case_id'
    template_name = 'case/case_detail.html'


class CaseCreateView(ConfiguredModelFormMixin, generic.CreateView):
    model = models.Case
    form_class = forms.CaseModelForm
    template_name = 'case/case_create.html'
