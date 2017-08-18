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


class TrademarkListView(DataTablesListView):
    dt_config = datatables.TrademarkDataTable
    model = models.Trademark
    template_name = 'trademark/trademark_list.html'


class TrademarkRelatedEntityView(RelatedEntityView):
    model = models.Trademark
    pk_url_kwarg = 'trademark_id'
    template_name = 'trademark/trademark_detail.html'

    def get_related_form(self):
        if self.current_entity_name == 'case.case':
            # 将client field的初始值设置为当前trademark关联的client
            self.object.client = self.main_object.client

            form = super().get_related_form()

            # 将client的选择范围限制在当前trademark关联的client上
            form.fields['client'].queryset = models.Client.objects.filter(
                id=self.main_object.client_id
            )
        else:
            form = super().get_related_form()

        return form


class TrademarkCreateView(FormMessageMixin, ConfiguredModelFormMixin, generic.CreateView):
    model = models.Trademark
    template_name = 'trademark/trademark_create.html'


class TrademarkDisableView(DisablementView):
    model = models.Trademark
    pk_url_kwarg = 'trademark_id'

    def validate(self):
        if any(case.enabled for case in self.object.case_set.all()):
            raise ValidationError(
                '不能删除该商标：该商标具有关联的案件',
                code='invalid'
            )

        if any(tmn.enabled for tmn in self.object.trademarknation_set.all()):
            raise ValidationError(
                '不能删除该商标：该商标具有关联的商标国家注册',
                code='invalid'
            )


class TrademarkNationListView(DataTablesListView):
    dt_config = datatables.TrademarkNationDataTable
    model = models.TrademarkNation
    template_name = 'trademarknation/trademarknation_list.html'


class TrademarkNationRelatedEntityView(RelatedEntityView):
    model = models.TrademarkNation
    pk_url_kwarg = 'trademarknation_id'
    template_name = 'trademarknation/trademarknation_detail.html'

    def get_related_form(self):
        form = super().get_related_form()

        if self.current_entity_name == 'case.subcase':
            form.fields['case'].queryset = self.main_object.trademark.case_set

        return form


class TrademarkNationCreateView(FormMessageMixin, ConfiguredModelFormMixin, generic.CreateView):
    model = models.TrademarkNation
    template_name = 'trademarknation/trademarknation_create.html'


class TrademarkNationDisableView(DisablementView):
    model = models.TrademarkNation
    pk_url_kwarg = 'trademarknation_id'

    def validate(self):
        if any(subcase.enabled for subcase in self.object.subcase_set.all()):
            raise ValidationError(
                '不能删除该商标：该商标具有关联的分案',
                code='invalid'
            )
