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
                '不能删除该待付款项：该应付款项具有关联的已付款项',
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

    def get_form(self):
        """
        : 为了简化保证数据完整性的业务逻辑，这里要求payable不能更改
        :return: form instance
        """
        form = super().get_form()
        if not self.is_related():
            form.fields['payable'].disabled = True
        return form


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

    def validate(self):
        # 判断是否有关联的PaymentLink存在
        if any(p.enabled for p in self.object.paymentlink_set.all()):
            raise ValidationError(
                '不能删除该已付款项：该已付款项具有关联的转移已付款项',
                code='invalid'
            )
        super().validate()


class PaymentLinkListView(DataTablesListView):
    dt_config = datatables.PaymentLinkDataTable
    model = models.PaymentLink
    template_name = 'purchase/payment_link_list.html'


class PaymentLinkRelatedEntityView(RelatedEntityView):
    model = models.PaymentLink
    pk_url_kwarg = 'paymentlink_id'
    template_name = 'purchase/payment_link_detail.html'


class PaymentLinkCreateView(FormMessageMixin, ConfiguredModelFormMixin, generic.CreateView):
    model = models.PaymentLink
    template_name = 'purchase/payment_link_create.html'


class PaymentLinkDisableView(DisablementView):
    model = models.PaymentLink
    pk_url_kwarg = 'paymentlink_id'
