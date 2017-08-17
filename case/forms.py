# -*- coding: utf-8 -*-

from django import forms

from utils.formfield.forms import ModelFormFieldSupportMixin
from utils.formfield.fields import ModelFormField

from . import models
from base import models as base_models


class ApplicationModelForm(forms.ModelForm):
    class Meta:
        model = models.Application
        fields = ['no', 'name', 'applicant', 'app_date']
        widgets = {
            'app_date': forms.TextInput(attrs={
                'data-provide': 'datepicker',
                'data-date-format': 'yyyy-mm-dd',
            }),
        }


class ContractModelForm(forms.ModelForm):
    class Meta:
        model = models.Contract
        fields = ['no', 'contractor_name', 'contractor_tel', 'contractor_mobile',
                  'contractor_email', 'contractor_qq', 'signed_date']
        widgets = {
            'signed_date': forms.TextInput(attrs={
                'data-provide': 'datepicker',
                'data-date-format': 'yyyy-mm-dd',
            }),
        }


class SubCaseModelForm(forms.ModelForm):
    class Meta:
        model = models.SubCase
        fields = ['name', 'closed', 'agent', 'case', 'entry_country',
                  'category', 'stage', 'desc']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # 设置enabled_objects, 同时限定is_agent=1
        self.fields['agent'].queryset = base_models.Client.enabled_objects.filter(is_agent=1)
        self.fields['case'].queryset = models.Case.enabled_objects
        self.fields['stage'].queryset = models.Stage.enabled_objects
        self.fields['entry_country'].queryset = base_models.Country.enabled_objects

        self.fields['category'].choices = models.Category.get_choices()


class CaseModelForm(ModelFormFieldSupportMixin, forms.ModelForm):
    application = ModelFormField(
        ApplicationModelForm,
        required=False,
        title="关联申请",
        prefix='app',
        using_template=True,
    )
    contract = ModelFormField(
        ContractModelForm,
        required=False,
        title='关联合同',
        prefix='contract',
        using_template=True,
    )

    class Meta:
        model = models.Case
        fields = ['name', 'archive_no', 'closed', 'client', 'owner',
                  'category', 'stage', 'desc']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if hasattr(self.instance, 'application'):
            # 根据application的enabled状态
            # 设置formfield的disabled状态
            if not self.instance.application.enabled:
                self.fields['application'].disabled = True

        if hasattr(self.instance, 'contract'):
            # 根据contract的enabled状态
            # 设置formfield的disabled状态
            if not self.instance.contract.enabled:
                self.fields['contract'].disabled = True

        self.fields['client'].queryset = base_models.Client.enabled_objects
        self.fields['owner'].queryset = base_models.Owner.enabled_objects
        # self.fields['category'].queryset = models.Category.enabled_objects
        self.fields['stage'].queryset = models.Stage.enabled_objects

        self.fields['category'].choices = models.Category.get_choices()
