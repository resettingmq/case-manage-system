from django.views import generic
from django.core.exceptions import ValidationError

from utils.views import DataTablesListView, InfoboxMixin, ConfiguredModelFormMixin,\
    RelatedEntityView, DisablementView, FormMessageMixin
from . import models, datatables

# Create your views here.


class IndexView(generic.TemplateView):
    template_name = 'base/index.html'
    view_name = 'index'


class ClientListView(DataTablesListView):
    dt_config = datatables.ClientDataTable
    model = models.Client
    template_name = 'base/client_list.html'


class ClientRelatedEntityView(RelatedEntityView):
    model = models.Client
    pk_url_kwarg = 'client_id'
    fields = ['name', 'is_agent', 'tel', 'mobile', 'fax', 'state', 'city',
              'address', 'postal_code', 'currency', 'country', 'desc']
    template_name = 'base/client_detail.html'


class ClientCreateView(FormMessageMixin, ConfiguredModelFormMixin, generic.CreateView):
    model = models.Client
    template_name = 'base/client_create.html'


class ClientDisableView(DisablementView):
    model = models.Client
    pk_url_kwarg = 'client_id'

    def validate(self):
        if any(case.enabled for case in self.object.case_set.all()):
            raise ValidationError(
                '不能删除该客户：该客户具有关联的案件',
                code='invalid'
            )
        if any(ac.enabled for ac in self.object.agent_subcase.all()):
            raise ValidationError(
                '不能删除该客户：该客户具有关联的代理分案',
                code='invalid'
            )
        super().validate()
