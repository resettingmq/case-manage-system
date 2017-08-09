import os
from decimal import Decimal
from collections import OrderedDict

from django.db import models
from django.conf import settings
from django.urls import reverse
from django.utils.functional import cached_property

from base.models import CommonFieldMixin, DescriptionFieldMixin, FakerMixin, EnabledEntityManager

BASE_DIR = settings.BASE_DIR


class ExpenseType(FakerMixin, CommonFieldMixin, DescriptionFieldMixin):
    name = models.CharField('支出类型', max_length=50)

    data_path = os.path.join(BASE_DIR, 'data/expense_type.json')

    objects = models.Manager()
    enabled_objects = EnabledEntityManager()

    class Meta:
        verbose_name = '支出类型'
        verbose_name_plural = '支出类型'

    def __str__(self):
        return self.name


class Expense(CommonFieldMixin, DescriptionFieldMixin):
    amount = models.DecimalField('支出金额', max_digits=10, decimal_places=2)
    exchange_rate = models.DecimalField(
        '汇率',
        max_digits=8,
        decimal_places=4,
        default=Decimal('1'),
    )
    incurred_date = models.DateField('支出日期', null=True, blank=True)

    currency = models.ForeignKey(
        'base.Currency',
        verbose_name='货币',
        default='CNY',
        on_delete=models.SET_NULL,
        null=True
    )
    expense_type = models.ForeignKey(
        ExpenseType,
        verbose_name='支出类型',
        on_delete=models.SET_NULL,
        null=True
    )
    subcase = models.ForeignKey(
        'case.SubCase',
        verbose_name='关联分案件',
        on_delete=models.SET_NULL,
        null=True
    )
    payment = models.OneToOneField(
        'purchase.Payment',
        verbose_name='关联已付款项',
        related_name='transfer_charge',
        on_delete=models.SET_NULL,
        null=True
    )
    receipts = models.OneToOneField(
        'sale.Receipts',
        verbose_name='关联已收款项',
        related_name='transfer_charge',
        on_delete=models.SET_NULL,
        null=True
    )

    objects = models.Manager()
    enabled_objects = EnabledEntityManager()

    modelform_class = 'expense.forms.ExpenseModelForm'
    datatables_class = 'expense.datatables.ExpenseDataTable'
    related_entity_config = {}

    class Meta:
        verbose_name = '支出'
        verbose_name_plural = '支出'

    def __str__(self):
        return '{}{}'.format(self.currency_id, self.amount)

    def get_absolute_url(self):
        return reverse('expense:detail', kwargs={'expense_id': self.id})

    def get_deletion_url(self):
        return reverse('expense:disable', kwargs={'expense_id': self.id})

    def get_deletion_success_url(self):
        return reverse('expense:detail', kwargs={'expense_id': self.id})

    @classmethod
    def get_related_entity_config(cls):
        if cls.related_entity_config is not None:
            return cls.related_entity_config

    def get_detail_info(self):
        detail_info = {}
        desc = OrderedDict()
        detail_info['title'] = '金额：{}'.format(self.amount)
        detail_info['sub_title'] = self.expense_type.name
        desc['汇率'] = self.exchange_rate or '未设置'
        desc['货币'] = self.currency.name_chs
        desc['日期'] = self.incurred_date or '未指定'
        if self.receipts:
            desc['关联已收款项'] = '{}{}-{}'.format(
                self.receipts.currency_id,
                self.receipts.amount,
                self.receipts.received_date
            )
        if self.payment:
            desc['关联已付款项'] = '{} {}-{}'.format(
                self.payment.currency_id,
                self.payment.amount,
                self.payment.paid_date
            )
        if self.subcase:
            desc['关联分案件'] = self.subcase.name

        detail_info['desc'] = desc
        detail_info['enabled'] = self.enabled

        return detail_info

    @cached_property
    def amount_cny(self):
        if self.currency_id == 'CNY':
            return self.amount
        else:
            return self.amount * self.exchange_rate
