import os
from django.db import models
from django.conf import settings
from django.urls import reverse

from base.models import CommonFieldMixin, DescriptionFieldMixin, FakerMixin
from base.models import Client, Country

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
    is_private = models.BooleanField(default=False)
    settled = models.BooleanField(default=False)
    closed = models.BooleanField(default=False)

    client = models.ForeignKey('base.Client', on_delete=models.SET_NULL, null=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    stage = models.ForeignKey(Stage, on_delete=models.SET_NULL, null=True)
    entry_country = models.ForeignKey('base.Country', on_delete=models.SET_NULL, null=True)

    datatables_class = 'case.views.CaseDataTable'
    modelform_class = 'case.forms.CaseModelForm'
    related_entity_config = {}

    faker_fields = {
        'name': 'sentence',
        'archive_no': 'isbn13',
        'is_private': 'pybool',
        'settled': 'pybool',
        'closed': 'pybool',
        'client': Client,
        'category': Category,
        'stage': Stage,
        'entry_country': Country,
        'desc': 'paragraph'
    }

    form_fields = ['name', 'archive_no', 'is_private', 'closed', 'client',
                   'category', 'stage', 'entry_country', 'desc']

    def __str__(self):
        return 'Case: {}'.format(self.name)

    def get_absolute_url(self):
        return reverse('case:case_detail', kwargs={'case_id': self.id})

    def get_detail_info(self):
        detail_info = {}
        desc = {}
        detail_info['title'] = self.name
        detail_info['sub_title'] = self.client.name
        desc['进入国家'] = self.entry_country.name_chs
        desc['分类'] = self.category.name
        desc['阶段'] = self.stage.name
        detail_info['desc'] = desc

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
