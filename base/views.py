from django.views import generic

from utils.views import DataTablesListView, InfoboxMixin, RelatedEntityView, DisablementView
from utils.utils import ModelDataTable, DataTablesColumn
from . import models

# Create your views here.


class ClientDataTable(ModelDataTable):
    name = DataTablesColumn()
    country__name_chs = DataTablesColumn()
    country__continent__name_chs = DataTablesColumn('国家名')

    dt_serverSide = True
    dt_processing = True
    # serverSide为True的情况下，
    # dt_ajax为None(ajax: null)的情况下，是对当前url发出ajax请求
    # serverSide为False的情况下，
    # 需要将dt_ajax设置为'.'或'./'来实现对当前url发出ajax请求
    dt_ajax = './'
    dt_rowId = 'id'

    class Meta:
        model = models.Client
        fields = ['is_agent']
        column_order = ['country__continent__name_chs', 'name', 'is_agent', 'country__name_chs']
        detail_url_format = '/client/{}'


class IndexView(InfoboxMixin, generic.TemplateView):
    template_name = 'base/index.html'
    view_name = 'index'


class ClientListView(DataTablesListView):
    dt_config = ClientDataTable
    model = models.Client
    template_name = 'base/client_list.html'

#
# class ClientDetailView(generic.UpdateView):
#     model = models.Client
#     pk_url_kwarg = 'client_id'
#     fields = ['name', 'is_agent', 'tel', 'mobile', 'fax', 'state', 'city',
#               'address', 'postal_code', 'currency', 'country', 'desc']
#     template_name = 'base/client_detail.html'


class ClientRelatedEntityView(RelatedEntityView):
    model = models.Client
    pk_url_kwarg = 'client_id'
    fields = ['name', 'is_agent', 'tel', 'mobile', 'fax', 'state', 'city',
              'address', 'postal_code', 'currency', 'country', 'desc']
    template_name = 'base/client_detail.html'


class ClientCreateView(generic.CreateView):
    model = models.Client
    fields = ['name', 'is_agent', 'tel', 'mobile', 'fax', 'state', 'city',
              'address', 'postal_code', 'currency', 'country', 'desc']
    template_name = 'base/client_create.html'


class ClientDisableView(DisablementView):
    model = models.Client
    pk_url_kwarg = 'client_id'
