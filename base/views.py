from django.views import generic
from django.core.exceptions import ValidationError
from django.apps import apps

from utils.views import DataTablesListView, InfoboxMixin, ConfiguredModelFormMixin,\
    RelatedEntityView, DisablementView, FormMessageMixin

from . import models, datatables
from case import models as case_models

# Create your views here.


class IndexView(generic.TemplateView):
    template_name = 'base/index.html'
    # view_name = 'index'
    infobox_list = ['base.client', 'case.case', 'case.subcase',
                    'base.trademark', 'base.trademarknation',
                    'base.pattern', 'base.patternnation',
                    'sale.receivable', 'sale.receipts',
                    'purchase.payable', 'purchase.payment',
                    'income.income', 'expense.expense']

    def get_context_data(self, **kwargs):
        info = dict()
        for entity_name in self.infobox_list:
            model = apps.get_model(entity_name)
            model_name = model._meta.model_name
            info[model_name] = dict()
            info[model_name]['count'] = model.enabled_objects.count()

        kwargs.update(info=info)

        return super().get_context_data(**kwargs)


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
            # 改为在_post_save()中根据trademark/pattern的client_id设置case.client_id
            # form.fields['client'].queryset = models.Client.objects.filter(
            #     id=self.main_object.client_id
            # )

            # 将category的选择范围限定在商标相关的category
            form.fields['category'].choices = case_models.Category.get_choices(parent=1)
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
            # 在subcase create form中
            # case的取值范围应该是trademarknation对应trademark的case_set
            form.fields['case'].queryset = self.main_object.trademark.case_set

            # 将category范围限制在trademark相关category
            form.fields['category'].choices = case_models.Category.get_choices(parent=1)

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
                '不能删除该商标-国家：该商标-国家具有关联的分案',
                code='invalid'
            )

    def disable(self):
        # 首先将所有相关联的trademarknationnice disable
        for tmnn in self.object.trademarknationnice_set.filter(enabled=True).all():
            tmnn.enabled = False
            tmnn.save()
        super().disable()


class TrademarkNationNiceRelatedEntityView(RelatedEntityView):
    model = models.TrademarkNationNice
    pk_url_kwarg = 'trademarknationnice_id'
    template_name = 'trademarknationnice/trademarknationnice_detail.html'


class TrademarkNationNiceDisableView(DisablementView):
    model = models.TrademarkNationNice
    pk_url_kwarg = 'trademarknationnice_id'


class PatternListView(DataTablesListView):
    dt_config = datatables.PatternDataTable
    model = models.Pattern
    template_name = 'pattern/pattern_list.html'


class PatternRelatedEntityView(RelatedEntityView):
    model = models.Pattern
    pk_url_kwarg = 'pattern_id'
    template_name = 'pattern/pattern_detail.html'

    def get_related_form(self):
        if self.current_entity_name == 'case.case':
            # 将client field的初始值设置为当前trademark关联的client
            self.object.client = self.main_object.client

            form = super().get_related_form()

            # 将client的选择范围限制在当前trademark关联的client上
            # 改为在_post_save()中根据trademark/pattern的client_id设置case.client_id
            # form.fields['client'].queryset = models.Client.objects.filter(
            #     id=self.main_object.client_id
            # )

            # 将category的选择范围限定在专利相关的category
            form.fields['category'].choices = case_models.Category.get_choices(parent=2)
        else:
            form = super().get_related_form()

        return form


class PatternCreateView(FormMessageMixin, ConfiguredModelFormMixin, generic.CreateView):
    model = models.Pattern
    template_name = 'pattern/pattern_create.html'


class PatternDisableView(DisablementView):
    model = models.Pattern
    pk_url_kwarg = 'pattern_id'

    def validate(self):
        if any(case.enabled for case in self.object.case_set.all()):
            raise ValidationError(
                '不能删除该专利：该专利具有关联的案件',
                code='invalid'
            )

        if any(pn.enabled for pn in self.object.patternnation_set.all()):
            raise ValidationError(
                '不能删除该专利：该商标具有关联的专利国家注册',
                code='invalid'
            )


class PatternNationListView(DataTablesListView):
    dt_config = datatables.PatternNationDataTable
    model = models.PatternNation
    template_name = 'patternnation/patternnation_list.html'


class PatternNationRelatedEntityView(RelatedEntityView):
    model = models.PatternNation
    pk_url_kwarg = 'patternnation_id'
    template_name = 'patternnation/patternnation_detail.html'

    def get_related_form(self):
        form = super().get_related_form()

        if self.current_entity_name == 'case.subcase':
            # 在subcase create form中
            # case的取值范围应该是patternnation对应pattern的case_set
            form.fields['case'].queryset = self.main_object.pattern.case_set
            # 将category范围限制在pattern相关category
            form.fields['category'].choices = case_models.Category.get_choices(parent=2)

        return form


class PatternNationCreateView(FormMessageMixin, ConfiguredModelFormMixin, generic.CreateView):
    model = models.PatternNation
    template_name = 'patternnation/patternnation_create.html'


class PatternNationDisableView(DisablementView):
    model = models.PatternNation
    pk_url_kwarg = 'patternnation_id'

    def validate(self):
        if any(subcase.enabled for subcase in self.object.subcase_set.all()):
            raise ValidationError(
                '不能删除该专利-国家：该专利-国家具有关联的分案',
                code='invalid'
            )
