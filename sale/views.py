from django.views import generic
from django.core.exceptions import ValidationError

from utils.views import DataTablesListView, ConfiguredModelFormMixin,\
    RelatedEntityView, DisablementView

from . import models, datatables

# Create your views here.


class ReceivableListView(DataTablesListView):
    dt_config = datatables.ReceivableDataTable
    model = models.Receivable
    template_name = 'sale/receivable_list.html'


class ReceivableRelatedEntityView(RelatedEntityView):
    model = models.Receivable
    pk_url_kwarg = 'receivable_id'
    template_name = 'sale/receivable_detail.html'


class ReceivableCreateView(ConfiguredModelFormMixin, generic.CreateView):
    model = models.Receivable
    template_name = 'sale/receivable_create.html'


class ReceivableDisableView(DisablementView):
    model = models.Receivable
    pk_url_kwarg = 'receivable_id'

    def validate(self):
        if any(rt.enabled for rt in self.object.receipts_set.all()):
            raise ValidationError(
                '不能删除该应收款项：该应收款项具有关联的已收款项',
                code='invalid'
            )
        super().validate()


class ReceiptsListView(DataTablesListView):
    dt_config = datatables.ReceiptsDataTable
    model = models.Receipts
    template_name = 'sale/receipts_list.html'


class ReceiptsRelatedEntityView(RelatedEntityView):
    model = models.Receipts
    pk_url_kwarg = 'receipts_id'
    template_name = 'sale/receipts_detail.html'

    def get_form(self):
        """
        : 为了简化保证数据完整性的业务逻辑，这里要求receivable不能更改
        :return: form instance
        """
        form = super().get_form()
        if not self.is_related():
            form.fields['receivable'].disabled = True
        return form


class ReceiptsCreateView(ConfiguredModelFormMixin, generic.CreateView):
    model = models.Receipts
    template_name = 'sale/receipts_create.html'


class ReceiptsDisableView(DisablementView):
    model = models.Receipts
    pk_url_kwarg = 'receipts_id'
