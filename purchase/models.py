from decimal import Decimal
from collections import OrderedDict

from django.db import models
from django.urls import reverse
from django.utils.functional import cached_property

from base.models import CommonFieldMixin, DescriptionFieldMixin, EnabledEntityManager


class Payable(CommonFieldMixin, DescriptionFieldMixin):
    no = models.CharField('待付款账单编号', max_length=100)
    received_date = models.DateField('账单收到日期')
    due_date = models.DateField('付款期限')
    amount = models.DecimalField('账单总金额', max_digits=10, decimal_places=2)
    unsettled_amount = models.DecimalField(
        '未付金额',
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )
    settled = models.BooleanField('是否付清', default=False)

    subcase = models.ForeignKey(
        'case.SubCase',
        verbose_name='关联分案',
        on_delete=models.SET_NULL,
        null=True
    )
    currency = models.ForeignKey(
        'base.Currency',
        verbose_name='货币',
        on_delete=models.SET_NULL,
        null=True
    )

    objects = models.Manager()
    enabled_objects = EnabledEntityManager()

    modelform_class = 'purchase.forms.PayableModelForm'
    datatables_class = 'purchase.datatables.PayableDataTable'
    related_entity_config = {
        'purchase.payment': {
            'query_path': 'payable',
            'verbose_name': '已付款项',
        }
    }

    class Meta:
        verbose_name = '待付款项'
        verbose_name_plural = '待付款项'

    def __str__(self):
        return '{}-{}{}'.format(self.no, self.currency_id, self.amount)

    def get_absolute_url(self):
        return reverse('payable:detail', kwargs={'payable_id': self.id})

    def get_deletion_url(self):
        return reverse('payable:disable', kwargs={'payable_id': self.id})

    def get_deletion_success_url(self):
        return reverse('payable:detail', kwargs={'payable_id': self.id})

    @classmethod
    def get_related_entity_config(cls):
        if cls.related_entity_config is not None:
            return cls.related_entity_config

    def get_detail_info(self):
        detail_info = {}
        desc = OrderedDict()
        detail_info['title'] = self.no or '未指定编号'
        detail_info['sub_title'] = '<a href="{}">{}</a>'.format(
            reverse('subcase:detail', kwargs={'subcase_id': self.subcase_id}),
            self.subcase.name
        )
        desc['所属案件'] = '<a href="{}">{}</a>'.format(
            reverse('case:detail', kwargs={'case_id': self.subcase.case_id}),
            self.subcase.case.name
        )
        desc['金额'] = self.amount
        desc['未付金额'] = self.unsettled_amount
        desc['货币'] = self.currency.name_chs
        desc['付款期限'] = self.due_date or '未指定'
        desc['账单收到日期'] = self.received_date or '未指定'
        detail_info['desc'] = desc
        detail_info['enabled'] = self.enabled

        return detail_info


class Payment(CommonFieldMixin, DescriptionFieldMixin):
    amount = models.DecimalField('已付款金额', max_digits=10, decimal_places=2)
    exchange_rate = models.DecimalField('付款汇率', max_digits=8, decimal_places=4)
    paid_date = models.DateField('付款日期')

    currency = models.ForeignKey(
        'base.Currency',
        verbose_name='付款货币',
        on_delete=models.SET_NULL,
        null=True
    )
    payable = models.ForeignKey(
        Payable,
        verbose_name='应付款账单',
        on_delete=models.SET_NULL,
        null=True
    )

    objects = models.Manager()
    enabled_objects = EnabledEntityManager()

    modelform_class = 'purchase.forms.PaymentModelForm'
    datatables_class = 'purchase.datatables.PaymentDataTable'
    related_entity_config = {
        'purchase.paymentlink': {
            'query_path': 'payment',
            'verbose_name': '转移'
        }
    }

    class Meta:
        verbose_name = '已付款项'
        verbose_name_plural = '已付款项'

    def __str__(self):
        return '{}{}-{}'.format(self.currency_id, self.amount, self.paid_date)

    def get_absolute_url(self):
        return reverse('payment:detail', kwargs={'payment_id': self.id})

    def get_deletion_url(self):
        return reverse('payment:disable', kwargs={'payment_id': self.id})

    def get_deletion_success_url(self):
        return reverse('payment:detail', kwargs={'payment_id': self.id})

    @classmethod
    def get_related_entity_config(cls):
        if cls.related_entity_config is not None:
            return cls.related_entity_config

    def get_detail_info(self):
        detail_info = {}
        desc = OrderedDict()
        detail_info['title'] = '金额：{}'.format(self.amount)
        detail_info['sub_title'] = ''
        desc['付款汇率'] = self.exchange_rate or '未设置'
        desc['货币'] = self.currency.name_chs
        desc['付款日期'] = self.paid_date or '未指定'
        desc['手续费(人民币)'] = self.transfer_charge.amount or '未指定'
        desc['已转移金额'] = self.linked_amount
        desc['未转移金额'] = self.unlinked_amount
        desc['所属待付账单'] = '<a href="{}">{}</a>'.format(
            reverse('payable:detail', kwargs={'payable_id': self.payable_id}),
            self.payable.no
        )
        desc['所属分案'] = '<a href="{}">{}</a>'.format(
            reverse('subcase:detail', kwargs={'subcase_id': self.payable.subcase_id}),
            self.payable.subcase.name
        )
        desc['所属案件'] = '<a href="{}">{}</a>'.format(
            reverse('case:detail', kwargs={'case_id': self.payable.subcase.case_id}),
            self.payable.subcase.case.name
        )

        detail_info['desc'] = desc
        detail_info['enabled'] = self.enabled

        return detail_info

    @cached_property
    def amount_cny(self):
        if self.currency_id == 'CNY':
            return self.amount
        else:
            return self.amount * self.exchange_rate

    @cached_property
    def linked_amount(self):
        return sum(link.amount for link in self.paymentlink_set.filter(enabled=1).all())

    @cached_property
    def unlinked_amount(self):
        return self.amount - self.linked_amount

    @cached_property
    def unlinked_amount_cny(self):
        return self.unlinked_amount * self.exchange_rate


class PaymentLink(CommonFieldMixin, DescriptionFieldMixin):
    amount = models.DecimalField('转移金额', max_digits=10, decimal_places=2)

    payment = models.ForeignKey(
        Payment,
        verbose_name='已付账单',
        on_delete=models.SET_NULL,
        null=True
    )
    subcase = models.ForeignKey(
        'case.SubCase',
        verbose_name='转移目标(分案件)',
        on_delete=models.SET_NULL,
        null=True
    )

    objects = models.Manager()
    enabled_objects = EnabledEntityManager()

    modelform_class = 'purchase.forms.PaymentLinkModelForm'
    datatables_class = 'purchase.datatables.PaymentLinkDataTable'
    related_entity_config = {}

    class Meta:
        verbose_name = '已付款转移'
        verbose_name_plural = '已付款转移'

    def __str__(self):
        return '转移已付款项: {}'.format(self.amount)

    def get_absolute_url(self):
        return reverse('paymentlink:detail', kwargs={'paymentlink_id': self.id})

    def get_deletion_url(self):
        return reverse('paymentlink:disable', kwargs={'paymentlink_id': self.id})

    def get_deletion_success_url(self):
        return reverse('paymentlink:detail', kwargs={'paymentlink_id': self.id})

    @classmethod
    def get_related_entity_config(cls):
        if cls.related_entity_config is not None:
            return cls.related_entity_config

    def get_detail_info(self):
        detail_info = {}
        desc = OrderedDict()
        detail_info['title'] = '金额：{}'.format(self.amount)
        detail_info['sub_title'] = ''
        desc['关联已付款金额'] = '<a href="{}">{}</a>'.format(
            reverse('payment:detail', kwargs={'payment_id': self.payment_id}),
            self.payment.amount
        )
        desc['关联已付款货币'] = self.payment.currency.name_chs
        desc['关联分案'] = '<a href="{}">{}</a>'.format(
            reverse('subcase:detail', kwargs={'subcase_id': self.subcase_id}),
            self.subcase.name
        )

        detail_info['desc'] = desc
        detail_info['enabled'] = self.enabled

        return detail_info

    @cached_property
    def amount_cny(self):
        if self.payment.currency_id == 'CNY':
            return self.amount
        else:
            return self.amount * self.payment.exchange_rate
