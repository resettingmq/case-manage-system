from django.views import generic
from django.core.exceptions import ValidationError

from utils.utils import ModelDataTable, DataTablesColumn
from utils.views import DataTablesListView, ConfiguredModelFormMixin,\
    RelatedEntityView, DisablementView, FormMessageMixin

from . import models, forms, datatables

# Create your views here.


class CaseListView(DataTablesListView):
    dt_config = datatables.CaseDataTable
    model = models.Case
    template_name = 'case/case_list.html'


class CaseRelatedEntityView(RelatedEntityView):
    model = models.Case
    form_class = forms.CaseModelForm
    pk_url_kwarg = 'case_id'
    template_name = 'case/case_detail.html'
    main_entity_extra_action = ['show_balance']

    def get_related_form(self):

        # 使subcase create form中初始category/stage与对应的case相同
        if self.current_entity_name == 'case.subcase':
            self.object.category = self.main_object.category
            self.object.stage = self.main_object.stage

            form = super().get_related_form()

            if self.main_object.trademark is not None:
                # 如果case关联的是trademark
                form.fields['category'].choices = models.Category.get_choices(parent=1)
                # 根据case限制可选的trademark nation(需要关联至同一个trademark)
                form.fields['trademarknation'].queryset = \
                    form.fields['trademarknation'].queryset.filter(
                        trademark_id=self.main_object.trademark_id
                    )
            elif self.main_object.pattern is not None:
                # 如果case关联的是pattern
                form.fields['category'].choices = models.Category.get_choices(parent=2)
                # 根据case限制可选的pattern nation(需要关联至同一个pattern)
                form.fields['patternnation'].queryset = \
                    form.fields['patternnation'].queryset.filter(
                        pattern_id=self.main_object.pattern_id
                    )
        else:
            form = super().get_related_form()

        return form


class CaseCreateView(FormMessageMixin, ConfiguredModelFormMixin, generic.CreateView):
    model = models.Case
    form_class = forms.CaseModelForm
    template_name = 'case/case_create.html'


class CaseDisableView(DisablementView):
    model = models.Case
    pk_url_kwarg = 'case_id'

    def validate(self):
        if any(subcase.enabled for subcase in self.object.subcase_set.all()):
            raise ValidationError(
                '不能删除该案件：该客户具有关联的分案',
                code='invalid'
            )

    def disable(self):
        # 在disable case之前，
        # 需要先disable相关联的application和contract
        if self.object.application:
            self.object.application.enabled = False
            self.object.application.save()
        if self.object.contract:
            self.object.contract.enabled = False
            self.object.contract.save()
        super().disable()


class SubCaseListView(DataTablesListView):
    dt_config = datatables.SubCaseDataTable
    model = models.SubCase
    template_name = 'case/subcase_list.html'


class SubCaseRelatedEntityView(RelatedEntityView):
    model = models.SubCase
    pk_url_kwarg = 'subcase_id'
    template_name = 'case/subcase_detail.html'


class SubCaseCreateView(FormMessageMixin, ConfiguredModelFormMixin, generic.CreateView):
    model = models.SubCase
    template_name = 'case/subcase_create.html'


class SubCaseDisableView(DisablementView):
    model = models.SubCase
    pk_url_kwarg = 'subcase_id'

    def validate(self):
        if any(rv.enabled for rv in self.object.receivable_set.all()):
            raise ValidationError(
                '不能删除该分案件：该分案件具有关联的待收款项',
                code='invalid',
            )

        if any(pa.enabled for pa in self.object.payable_set.all()):
            raise ValidationError(
                '不能删除该分案件：该分案件具有关联的待付款项',
                code='invalid',
            )

        if any(expense.enabled for expense in self.object.expense_set.all()):
            raise ValidationError(
                '不能删除该分案件：该分案件具有关联的其它支出',
                code='invalid',
            )
        # 判断是否有关联的PaymentLink存在
        if any(p.enabled for p in self.object.paymentlink_set.all()):
            raise ValidationError(
                '不能删除该已付款项：该已付款项具有关联的转移已付款项',
                code='invalid'
            )
        super().validate()
