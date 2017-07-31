# -*- coding: utf-8 -*-

from django.forms import ModelForm

from utils.formfield.forms import ModelFormFieldSupportMixin
from utils.formfield.fields import ModelFormField

from . import models


class ApplicationModelForm(ModelForm):
    class Meta:
        model = models.Application
        fields = ['no', 'name', 'applicant', 'app_date']


class CaseModelForm(ModelFormFieldSupportMixin, ModelForm):
    application = ModelFormField(
        ApplicationModelForm,
        title="关联合同",
        prefix='case',
        using_template=True,
    )

    class Meta:
        model = models.Case
        fields = ['name', 'archive_no', 'is_private', 'closed', 'client',
                  'category', 'stage', 'entry_country', 'desc']
