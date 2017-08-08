from django.views import generic
from django.core.exceptions import ValidationError

from utils.utils import ModelDataTable, DataTablesColumn
from utils.views import DataTablesListView, ConfiguredModelFormMixin,\
    RelatedEntityView, DisablementView

from . import models, forms, datatables

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


class CaseDisableView(DisablementView):
    model = models.Case
    pk_url_kwarg = 'case_id'


class SubCaseListView(DataTablesListView):
    dt_config = datatables.SubCaseDataTable
    model = models.SubCase
    template_name = 'case/subcase_list.html'


class SubCaseRelatedEntityView(RelatedEntityView):
    model = models.SubCase
    pk_url_kwarg = 'subcase_id'
    template_name = 'case/subcase_detail.html'


class SubCaseCreateView(ConfiguredModelFormMixin, generic.CreateView):
    model = models.SubCase
    template_name = 'case/subcase_create.html'

    def get_form(self, form_class=None):
        # 需要修改生成form，以限制agent的choice范围
        form = super().get_form(form_class)
        form.fields['agent'].queryset = form.fields['agent'].queryset.filter(is_agent=True)
        return form


class SubCaseDisableView(DisablementView):
    model = models.SubCase
    pk_url_kwarg = 'subcase_id'

    def validate(self):
        if len(self.object.expense_set.all()) != 0:
            raise ValidationError(
                '不能删除该分案件：该分案件具有关联的其它支出',
                code='invalid',
            )
        super().validate()
