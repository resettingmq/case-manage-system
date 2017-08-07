import os
from django.db import models
from django.conf import settings
from django.urls import reverse

from base.models import CommonFieldMixin, DescriptionFieldMixin, FakerMixin, EnabledEntityManager
from base.models import Client, Country, Owner

# Create your models here.

BASE_DIR = settings.BASE_DIR


class Stage(FakerMixin, CommonFieldMixin):
    name = models.CharField(max_length=100)

    data_path = os.path.join(BASE_DIR, 'data/case_stage.json')

    def __str__(self):
        return 'Case stage: {}'.format(self.name)


class Category(FakerMixin, CommonFieldMixin):
    name = models.CharField(max_length=100)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)

    data_path = os.path.join(BASE_DIR, 'data/case_category.json')

    class Meta:
        verbose_name_plural = 'categories'

    def __str__(self):
        return 'Case category: {}'.format(self.name)


class Case(FakerMixin, CommonFieldMixin, DescriptionFieldMixin):
    name = models.CharField(max_length=200)
    archive_no = models.CharField(max_length=100, null=True, blank=True)
    settled = models.BooleanField(default=False)
    closed = models.BooleanField(default=False)

    client = models.ForeignKey('base.Client', on_delete=models.SET_NULL, null=True)
    owner = models.ForeignKey('base.Owner', on_delete=models.SET_NULL, null=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    stage = models.ForeignKey(Stage, on_delete=models.SET_NULL, null=True)
    entry_country = models.ForeignKey('base.Country', on_delete=models.SET_NULL, null=True)

    objects = models.Manager()
    enabled_objects = EnabledEntityManager()

    datatables_class = 'case.views.CaseDataTable'
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
        'entry_country': Country,
        'desc': 'paragraph'
    }

    form_fields = ['name', 'archive_no', 'owner', 'closed', 'client',
                   'category', 'stage', 'entry_country', 'desc']

    def __str__(self):
        return 'Case: {}'.format(self.name)

    def get_absolute_url(self):
        return reverse('case:detail', kwargs={'case_id': self.id})

    def get_deletion_url(self):
        return reverse('case:disable', kwargs={'case_id': self.id})

    def get_deletion_success_url(self):
        return reverse('case:detail', kwargs={'case_id': self.id})

    def get_detail_info(self):
        detail_info = {}
        desc = {}
        detail_info['title'] = self.name
        detail_info['sub_title'] = self.client.name
        desc['进入国家'] = self.entry_country.name_chs
        desc['分类'] = self.category.name
        desc['阶段'] = self.stage.name
        detail_info['desc'] = desc
        detail_info['enabled'] = self.enabled

        return detail_info

    @classmethod
    def get_related_entity_config(self):
        if self.related_entity_config is not None:
            return self.related_entity_config


class Application(FakerMixin, CommonFieldMixin, DescriptionFieldMixin):
    no = models.CharField(max_length=100)
    name = models.CharField(max_length=300, null=True, blank=True)
    applicant = models.CharField(max_length=300, null=True, blank=True)
    app_date = models.DateField(null=True, blank=True)

    case = models.OneToOneField(Case, on_delete=models.SET_NULL, null=True)

    faker_fields = {
        'no': 'isbn13',
        'name': 'sentence',
        'applicant': 'name',
        'app_date': 'date',
        'case': Case
    }

    def __str__(self):
        return 'Application: {}-{}'.format(self.no, self.name)


class Contract(FakerMixin, CommonFieldMixin, DescriptionFieldMixin):
    no = models.CharField(max_length=100, null=True, blank=False)
    contractor_name = models.CharField(max_length=100, null=True, blank=True)
    contractor_tel = models.CharField(max_length=30, null=True, blank=True)
    contractor_mobile = models.CharField(max_length=30, null=True, blank=True)
    contractor_email = models.CharField(max_length=200, null=True, blank=True)
    contractor_qq = models.CharField(max_length=45, null=True, blank=True)
    signed_date = models.DateField(null=True, blank=True)

    case = models.OneToOneField(Case, on_delete=models.SET_NULL, null=True)

    faker_fields = {
        'no': 'isbn13',
        'contractor_name': 'name',
        'contractor_tel': 'phone_number',
        'contractor_mobile': 'phone_number',
        'contractor_email': 'email',
        'contractor_qq': 'ean8',
        'signed_date': 'date',
        'case': Case
    }

    def __str__(self):
        return 'Contract: {}-{}'.format(self.no, self.case.name)


class SubCase(FakerMixin, CommonFieldMixin, DescriptionFieldMixin):
    name = models.CharField('分案名', max_length=200)
    settled = models.BooleanField('款项结清', default=False)
    closed = models.BooleanField('结案', default=False)

    agent = models.ForeignKey(
        'base.Client',
        related_name='agent_subcase',
        verbose_name='代理',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    case = models.ForeignKey(
        Case,
        verbose_name='所属案件',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    stage = models.ForeignKey(
        Stage,
        verbose_name='所处阶段',
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
    }

    def __str__(self):
        return 'SubCase: {}'.format(self.name)

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
        desc = {}
        detail_info['title'] = self.name
        detail_info['sub_title'] = self.case.name
        desc['代理'] = self.agent.name
        desc['阶段'] = self.stage.name
        desc['结清款项'] = self.settled
        detail_info['desc'] = desc
        detail_info['enabled'] = self.enabled

        return detail_info
