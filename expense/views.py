from django.views import generic
from django.core.exceptions import ValidationError

from utils.views import DataTablesListView, ConfiguredModelFormMixin,\
    RelatedEntityView, DisablementView, FormMessageMixin

from . import models, datatables


class ExpenseListView(DataTablesListView):
    dt_config = datatables.ExpenseDataTable
    model = models.Expense
    template_name = 'expense/expense_list.html'


class ExpenseRelatedEntityView(RelatedEntityView):
    model = models.Expense
    pk_url_kwarg = 'expense_id'
    template_name = 'expense/expense_detail.html'


class ExpenseCreateView(FormMessageMixin, ConfiguredModelFormMixin, generic.CreateView):
    model = models.Expense
    template_name = 'expense/expense_create.html'


class ExpenseDisableView(DisablementView):
    model = models.Expense
    pk_url_kwarg = 'expense_id'

    def validate(self):
        # 不能直接删除与payment/receipts关联的expense
        # 应该从payment/receipts中直接修改
        if self.object.payment:
            raise ValidationError(
                '该支出款项为已付款项({})的手续费，请从该已付款项中设置，不能直接删除'.format(self.object.payment),
                code='invalid'
            )
        if self.object.receipts:
            raise ValidationError(
                '该支出款项为已收款项({})的手续费，请从该已收款项中设置，不能直接删除'.format(self.object.receipts),
                code='invalid'
            )
        super().validate()
