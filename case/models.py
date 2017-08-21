import os
import itertools
from collections import OrderedDict

from django.db import models
from django.conf import settings
from django.urls import reverse
from django.utils.functional import cached_property

from base.models import CommonFieldMixin, DescriptionFieldMixin, FakerMixin, EnabledEntityManager
from base.models import Client, Country, Owner

# Create your models here.

BASE_DIR = settings.BASE_DIR


class Stage(FakerMixin, CommonFieldMixin):
    name = models.CharField('名称', max_length=100)

    objects = models.Manager()
    enabled_objects = EnabledEntityManager()

    data_path = os.path.join(BASE_DIR, 'data/case_stage.json')

    class Meta:
        verbose_name = '案件阶段'
        verbose_name_plural = '案件阶段'

    def __str__(self):
        return '{}'.format(self.name)


class Category(FakerMixin, CommonFieldMixin):
    name = models.CharField('名称', max_length=100)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)

    objects = models.Manager()
    enabled_objects = EnabledEntityManager()

    data_path = os.path.join(BASE_DIR, 'data/case_category.json')

    class Meta:
        verbose_name = '案件分类'
        verbose_name_plural = '案件分类'

    def __str__(self):
        return '{}'.format(self.name)

    @classmethod
    def get_choices(cls, parent=None):
        """
        生成带有一级optgroup的HTML select options数据
        :param parent: 用于筛选返回结果中的类别，支持list或者单个int值
        :return: 
        """
        choices = []
        for c in cls.enabled_objects.all():
            if c.parent is not None:
                continue
            if parent and (isinstance(parent, list) and c.id not in parent or c.id != parent):
                # 筛选分类
                # 在Trademark/Pattern relatedView中会调用
                continue
            choices.append((c.name, [(child_c.id, child_c.name) for child_c in c.category_set.all()]))
        return choices


class Case(FakerMixin, CommonFieldMixin, DescriptionFieldMixin):
    name = models.CharField('案件名称', max_length=200)
    archive_no = models.CharField('档案号', max_length=100, null=True, blank=True)
    closed = models.BooleanField('结案', default=False)

    client = models.ForeignKey(
        'base.Client',
        verbose_name='客户',
        on_delete=models.SET_NULL,
        null=True
    )
    owner = models.ForeignKey(
        'base.Owner',
        verbose_name='所属部门',
        on_delete=models.SET_NULL,
        null=True
    )
    category = models.ForeignKey(
        Category,
        verbose_name='案件类型',
        on_delete=models.SET_NULL,
        null=True
    )
    stage = models.ForeignKey(
        Stage,
        verbose_name='所处阶段',
        on_delete=models.SET_NULL,
        null=True
    )
    trademark = models.ForeignKey(
        'base.Trademark',
        verbose_name='商标',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    pattern = models.ForeignKey(
        'base.Pattern',
        verbose_name='专利',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    objects = models.Manager()
    enabled_objects = EnabledEntityManager()

    datatables_class = 'case.datatables.CaseDataTable'
    modelform_class = 'case.forms.CaseModelForm'
    related_entity_config = {
        'case.subcase': {
            'query_path': 'case',
            'verbose_name': '分案信息',
        }
    }

    faker_fields = {
        'name': 'sentence',
        'archive_no': 'isbn13',
        'settled': 'pybool',
        'closed': 'pybool',
        'client': Client,
        'owner': Owner,
        'category': Category,
        'stage': Stage,
        'desc': 'paragraph'
    }

    class Meta:
        verbose_name = '案件'
        verbose_name_plural = '案件'

    def __str__(self):
        return '{}:{}'.format(self.archive_no, self.name)

    def get_absolute_url(self):
        return reverse('case:detail', kwargs={'case_id': self.id})

    def get_deletion_url(self):
        return reverse('case:disable', kwargs={'case_id': self.id})

    def get_deletion_success_url(self):
        return reverse('case:detail', kwargs={'case_id': self.id})

    def get_detail_info(self):
        detail_info = {}
        desc = OrderedDict()
        detail_info['title'] = self.name
        detail_info['sub_title'] = self.archive_no

        desc['客户'] = '<a href="{}">{}</a>'.format(
            reverse('client:detail', kwargs={'client_id': self.client_id}),
            self.client.name
        )
        desc['案件类型'] = self.category.name
        desc['所属阶段'] = self.stage.name
        desc['所属部门'] = self.owner.name
        desc['结案'] = '是' if self.closed else '否'
        detail_info['desc'] = desc
        detail_info['enabled'] = self.enabled

        return detail_info

    @classmethod
    def get_related_entity_config(cls):
        if cls.related_entity_config is not None:
            return cls.related_entity_config

    @cached_property
    def balance_amount_cny(self):
        balance = sum(
            subcase.receipts_sum_cny + subcase.income_sum_cny
            - (subcase.payment_sum_cny + subcase.expense_sum_cny + subcase.paymentlink_sum_cny)
            for subcase in self.subcase_set.filter(enabled=1).all()
        )

        return balance


class SubCase(FakerMixin, CommonFieldMixin, DescriptionFieldMixin):
    name = models.CharField('分案名', max_length=200)
    closed = models.BooleanField('结案', default=False)

    agent = models.ForeignKey(
        'base.Client',
        related_name='agent_subcase',
        verbose_name='代理',
        on_delete=models.SET_NULL,
        null=True,
    )
    case = models.ForeignKey(
        Case,
        verbose_name='所属案件',
        on_delete=models.SET_NULL,
        null=True,
    )
    category = models.ForeignKey(
        Category,
        verbose_name='案件类型',
        on_delete=models.SET_NULL,
        null=True
    )
    stage = models.ForeignKey(
        Stage,
        verbose_name='所处阶段',
        on_delete=models.SET_NULL,
        null=True,
    )
    trademarknation = models.ForeignKey(
        'base.TrademarkNation',
        verbose_name='商标-进入国家',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    patternnation = models.ForeignKey(
        'base.PatternNation',
        verbose_name='专利-进入国家',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    objects = models.Manager()
    enabled_objects = EnabledEntityManager()

    modelform_class = 'case.forms.SubCaseModelForm'
    datatables_class = 'case.datatables.SubCaseDataTable'
    related_entity_config = {
        'sale.receivable': {
            'query_path': 'subcase',
            'verbose_name': '待收款项',
        },
        'purchase.payable': {
            'query_path': 'subcase',
            'verbose_name': '待付款项',
        },
        'expense.expense': {
            'query_path': 'subcase',
            'verbose_name': '其它支出'
        },
        'income.income': {
            'query_path': 'subcase',
            'verbose_name': '其它收入'
        },
    }

    class Meta:
        verbose_name = '分案'
        verbose_name_plural = '分案'

    def __str__(self):
        return '分案: {}'.format(self.name)

    def get_absolute_url(self):
        return reverse('subcase:detail', kwargs={'subcase_id': self.id})

    def get_deletion_url(self):
        return reverse('subcase:disable', kwargs={'subcase_id': self.id})

    def get_deletion_success_url(self):
        return reverse('subcase:detail', kwargs={'subcase_id': self.id})

    @classmethod
    def get_related_entity_config(cls):
        if cls.related_entity_config is not None:
            return cls.related_entity_config

    def get_detail_info(self):
        detail_info = {}
        desc = OrderedDict()
        detail_info['title'] = self.name
        detail_info['sub_title'] = '<a href="{}">{}</a>'.format(
            reverse('case:detail', kwargs={'case_id': self.case_id}),
            self.case.name
        )
        desc['代理'] = '<a href="{}">{}</a>'.format(
            reverse('client:detail', kwargs={'client_id': self.agent_id}),
            self.agent.name
        )
        desc['案件类型'] = self.category.name
        desc['所处阶段'] = self.stage.name
        if self.trademarknation:
            desc['商标(国家)'] = '<a href="{}">{}</a>'.format(
                reverse('trademarknation:detail', kwargs={'trademarknation_id': self.trademarknation_id}),
                self.trademarknation
            )
        if self.patternnation:
            desc['专利(国家)'] = '<a href="{}">{}</a>'.format(
                reverse('patternnation:detail', kwargs={'patternnation_id': self.patternnation_id}),
                self.patternnation
            )
        desc['结案'] = '是' if self.closed else '否'
        detail_info['desc'] = desc
        detail_info['enabled'] = self.enabled

        return detail_info

    @property
    def receipts_iter(self):
        # 因为这个iter要多次使用
        # 所以不能设置为cached_property
        # 注意要使用filter enabled=1
        return itertools.chain.from_iterable(rv.receipts_set.filter(enabled=1).all() for rv in self.receivable_set.all())

    @cached_property
    def receipts_sum_cny(self):
        # 所有关联receipts的总金额
        # 减去transfer_charge
        return sum(rv.amount_cny - rv.transfer_charge.amount for rv in self.receipts_iter)

    @property
    def payment_iter(self):
        # 因为这个iter要多次使用
        # 所以不能设置为cached_property
        # 注意要使用filter enabled=1
        return itertools.chain.from_iterable(pa.payment_set.filter(enabled=1).all() for pa in self.payable_set.all())

    @cached_property
    def payment_sum_cny(self):
        # 所有关联payment的总金额
        # 包含transfer_charge
        # 注意使用的是unlinked_amount_cny，表示当前payment未被转移的金额(CNY)
        return sum(pm.unlinked_amount_cny + pm.transfer_charge.amount for pm in self.payment_iter)

    @cached_property
    def paymentlink_sum_cny(self):
        # 注意要使用filter enabled=1
        return sum(plink.amount_cny for plink in self.paymentlink_set.filter(enabled=1).all())

    @cached_property
    def income_sum_cny(self):
        # 注意要使用filter enabled=1
        return sum(income.amount_cny for income in self.income_set.filter(enabled=1).all())

    @cached_property
    def expense_sum_cny(self):
        # 注意要使用filter enabled=1
        return sum(expense.amount_cny for expense in self.expense_set.filter(enabled=1).all())


class Contract(FakerMixin, CommonFieldMixin, DescriptionFieldMixin):
    no = models.CharField('合同编号', max_length=100)
    contractor_name = models.CharField('联系人姓名', max_length=100, null=True, blank=True)
    contractor_tel = models.CharField('联系人电话', max_length=30, null=True, blank=True)
    contractor_mobile = models.CharField('联系人手机', max_length=30, null=True, blank=True)
    contractor_email = models.CharField('联系人Email', max_length=200, null=True, blank=True)
    contractor_qq = models.CharField('联系人QQ', max_length=45, null=True, blank=True)
    signed_date = models.DateField('签字日期', null=True, blank=True)

    subcase = models.OneToOneField(
        SubCase,
        verbose_name='关联合同',
        on_delete=models.SET_NULL,
        null=True
    )

    faker_fields = {
        'no': 'isbn13',
        'contractor_name': 'name',
        'contractor_tel': 'phone_number',
        'contractor_mobile': 'phone_number',
        'contractor_email': 'email',
        'contractor_qq': 'ean8',
        'signed_date': 'date',
        'subcase': SubCase
    }

    def __str__(self):
        return '{}-{}'.format(self.no, self.contractor_name)
