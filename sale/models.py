from collections import OrderedDict
from decimal import Decimal

from django.db import models
from django.conf import settings
from django.urls import reverse

from base.models import CommonFieldMixin, DescriptionFieldMixin, FakerMixin

# Create your models here.

BASE_DIR = settings.BASE_DIR


class Receivable(CommonFieldMixin, DescriptionFieldMixin):
    no = models.CharField('待收款账单编号', max_length=100, null=True, blank=True)
    sent_date = models.DateField('发送日期', null=True, blank=True)
    sent = models.BooleanField('已发送', default=False)
    due_date = models.DateField('待收期限', null=True, blank=True)
    amount = models.DecimalField('待收金额', max_digits=10, decimal_places=2)
    unsettled_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )

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

    modelform_class = 'sale.forms.ReceivableModelForm'
    datatables_class = 'sale.datatables.ReceivableDataTable'
    related_entity_config = {
        'sale.receipts': {
            'query_path': 'receivable',
            'verbose_name': '已收款项'
        }
    }

    def __str__(self):
        return '{}-{}'.format(self.no, self.amount)

    def get_absolute_url(self):
        return reverse('receivable:detail', kwargs={'receivable_id': self.id})

    def get_deletion_url(self):
        return reverse('receivable:disable', kwargs={'receivable_id': self.id})

    def get_deletion_success_url(self):
        return reverse('receivable:detail', kwargs={'receivable_id': self.id})

    @classmethod
    def get_related_entity_config(cls):
        if cls.related_entity_config is not None:
            return cls.related_entity_config

    def get_detail_info(self):
        detail_info = {}
        desc = OrderedDict()
        detail_info['title'] = self.no or '未指定编号'
        detail_info['sub_title'] = getattr(self.subcase, 'name', '')
        desc['所属案件'] = self.subcase.case.name
        desc['金额'] = self.amount
        desc['未收金额'] = self.unsettled_amount
        desc['货币'] = self.currency.name_chs
        desc['期限'] = self.due_date or '未指定'
        desc['发送日期'] = self.sent_date or '未指定'
        desc['是否发送'] = self.sent
        detail_info['desc'] = desc
        detail_info['enabled'] = self.enabled

        return detail_info


class Receipts(CommonFieldMixin, DescriptionFieldMixin):
    amount = models.DecimalField('已收款金额', max_digits=10, decimal_places=2)
    exchange_rate = models.DecimalField('收款汇率', max_digits=8, decimal_places=4, null=True, blank=True)
    received_date = models.DateField('收款日期')
    transfer_charge = models.DecimalField(
        '手续费',
        max_digits=7,
        decimal_places=2,
        default=Decimal,
        null=True,
        blank=False
    )

    currency = models.ForeignKey(
        'base.Currency',
        verbose_name='收款货币',
        on_delete=models.SET_NULL,
        null=True
    )
    receivable = models.ForeignKey(
        Receivable,
        verbose_name='收款账单',
        on_delete=models.SET_NULL,
        null=True
    )
    deposit = models.ForeignKey(
        'income.Deposit',
        verbose_name='客户预存款',
        on_delete=models.SET_NULL,
        null=True
    )

    modelform_class = 'sale.forms.ReceiptsModelForm'
    datatables_class = 'sale.datatables.ReceiptsDataTable'
    related_entity_config = {}

    def __str__(self):
        return '{}-{}'.format(self.amount, self.received_date)

    def get_absolute_url(self):
        return reverse('receipts:detail', kwargs={'receipts_id': self.id})

    def get_deletion_url(self):
        return reverse('receipts:disable', kwargs={'receipts_id': self.id})

    def get_deletion_success_url(self):
        return reverse('receipts:detail', kwargs={'receipts_id': self.id})

    @classmethod
    def get_related_entity_config(cls):
        if cls.related_entity_config is not None:
            return cls.related_entity_config

    def get_detail_info(self):
        detail_info = {}
        desc = OrderedDict()
        detail_info['title'] = '金额：{}'.format(self.amount)
        detail_info['sub_title'] = ''
        desc['收款汇率'] = self.exchange_rate or '未设置'
        desc['货币'] = self.currency.name_chs
        desc['received_date'] = self.received_date or '未指定'
        desc['手续费'] = self.transfer_charge or '未指定'
        desc['所属待收账单'] = getattr(self.receivable, 'name', '未指定编号')

        detail_info['desc'] = desc
        detail_info['enabled'] = self.enabled

        return detail_info
