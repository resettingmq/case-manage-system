from django.views import generic
from django.core.exceptions import ValidationError

from utils.views import DataTablesListView, ConfiguredModelFormMixin,\
    RelatedEntityView, DisablementView, FormMessageMixin

from . import models, datatables


class PayableListView(DataTablesListView):
    dt_config = datatables.PayableDataTable
    model = models.Payable
    template_name = 'purchase/payable_list.html'


class PayableRelatedEntityView(RelatedEntityView):
    model = models.Payable
    pk_url_kwarg = 'payable_id'
    template_name = 'purchase/payable_detail.html'


class PayableCreateView(ConfiguredModelFormMixin, generic.CreateView):
    model = models.Payable
    template_name = 'purchase/payable_create.html'


class PayableDisableView(DisablementView):
    model = models.Payable
    pk_url_kwarg = 'payable_id'

    def validate(self):
        if any(p.enabled for p in self.object.payment_set.all()):
            raise ValidationError(
                '不能删除该应付款项：该应付款项具有关联的已付款项',
                code='invalid'
            )
            super().validate()


class PaymentListView(DataTablesListView):
    dt_config = datatables.PaymentDataTable
    model = models.Payment
    template_name = 'purchase/payment_list.html'


class PaymentRelatedEntityView(RelatedEntityView):
    model = models.Payment
    pk_url_kwarg = 'payment_id'
    template_name = 'purchase/payment_detail.html'


class PaymentCreateView(FormMessageMixin, ConfiguredModelFormMixin, generic.CreateView):
    model = models.Payment
    template_name = 'purchase/payment_create.html'


class PaymentDisableView(DisablementView):
    model = models.Payment
    pk_url_kwarg = 'payment_id'

    def disable(self):
        # 在禁用Payment之前，需要禁用关联的Expense
        if self.object.transfer_charge:
            self.object.transfer_charge.enabled = False
            self.object.transfer_charge.save()
        super().disable()
