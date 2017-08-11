import os
from decimal import Decimal
from collections import OrderedDict

from django.db import models
from django.conf import settings
from django.urls import reverse
from django.utils.functional import cached_property

from base.models import CommonFieldMixin, DescriptionFieldMixin, FakerMixin, EnabledEntityManager

BASE_DIR = settings.BASE_DIR


class Deposit(CommonFieldMixin, DescriptionFieldMixin):
    amount = models.DecimalField('预收款总额', max_digits=10, decimal_places=2)
    balance = models.DecimalField('预收款余额', max_digits=10, decimal_places=2,
                                  null=True, blank=False)
    received_date = models.DateField('收到日期')

    client = models.ForeignKey(
        'base.Client',
        verbose_name='客户',
        on_delete=models.SET_NULL,
        null=True
    )
    currency = models.ForeignKey(
        'base.Currency',
        verbose_name='货币',
        on_delete=models.SET_NULL,
        null=True
    )


class IncomeType(FakerMixin, CommonFieldMixin, DescriptionFieldMixin):
    name = models.CharField('收入类型', max_length=50)

    data_path = os.path.join(BASE_DIR, 'data/income_type.json')

    objects = models.Manager()
    enabled_objects = EnabledEntityManager()

    class Meta:
        verbose_name = '收入类型'
        verbose_name_plural = '收入类型'

    def __str__(self):
        return self.name


class Income(CommonFieldMixin, DescriptionFieldMixin):
    amount = models.DecimalField('收入金额', max_digits=10, decimal_places=2)
    exchange_rate = models.DecimalField(
        '汇率',
        max_digits=8,
        decimal_places=4,
        default=Decimal('1')
    )
    incurred_date = models.DateField('收入日期', null=True, blank=True)

    currency = models.ForeignKey(
        'base.Currency',
        verbose_name='货币',
        default='CNY',
        on_delete=models.SET_NULL,
        null=True
    )
    income_type = models.ForeignKey(
        IncomeType,
        verbose_name='收入类型',
        on_delete=models.SET_NULL,
        null=True
    )
    subcase = models.ForeignKey(
        'case.SubCase',
        verbose_name='关联分案件',
        on_delete=models.SET_NULL,
        null=True
    )

    objects = models.Manager()
    enabled_objects = EnabledEntityManager()

    modelform_class = 'income.forms.IncomeModelForm'
    datatables_class = 'income.datatables.IncomeDataTable'
    related_entity_config = {}

    class Meta:
        verbose_name = '其它收入'
        verbose_name_plural = '其它收入'

    def __str__(self):
        return '{}{}'.format(self.currency_id, self.amount)

    def get_absolute_url(self):
        return reverse('income:detail', kwargs={'income_id': self.id})

    def get_deletion_url(self):
        return reverse('income:disable', kwargs={'income_id': self.id})

    def get_deletion_success_url(self):
        return reverse('income:detail', kwargs={'income_id': self.id})

    @classmethod
    def get_related_entity_config(cls):
        if cls.related_entity_config is not None:
            return cls.related_entity_config

    def get_detail_info(self):
        detail_info = {}
        desc = OrderedDict()
        detail_info['title'] = '金额：{}'.format(self.amount)
        detail_info['sub_title'] = self.income_type.name
        desc['货币'] = self.currency.name_chs
        desc['汇率'] = self.exchange_rate or '未设置'
        desc['日期'] = self.incurred_date or '未指定'
        if self.subcase:
            desc['关联分案件'] = '<a href="{}">{}</a>'.format(
                reverse('subcase:detail', kwargs={'subcase_id': self.subcase_id}),
                self.subcase.name
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
