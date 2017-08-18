# -*- coding: utf-8 -*-

from django import forms

from utils.formfield.forms import ModelFormFieldSupportMixin
from utils.formfield.fields import ModelFormField

from . import models
from base import models as base_models


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


class SubCaseModelForm(ModelFormFieldSupportMixin, forms.ModelForm):
    contract = ModelFormField(
        ContractModelForm,
        required=False,
        title='关联合同',
        prefix='contract',
        using_template=True,
    )

    class Meta:
        model = models.SubCase
        fields = ['name', 'agent', 'case',
                  'category', 'stage', 'trademarknation', 'closed', 'desc']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if hasattr(self.instance, 'contract'):
            # 根据contract的enabled状态
            # 设置formfield的disabled状态
            if not self.instance.contract.enabled:
                self.fields['contract'].disabled = True

        # 设置enabled_objects, 同时限定is_agent=1
        self.fields['agent'].queryset = base_models.Client.enabled_objects.filter(is_agent=1)
        self.fields['case'].queryset = models.Case.enabled_objects
        self.fields['stage'].queryset = models.Stage.enabled_objects
        self.fields['trademarknation'].queryset = base_models.TrademarkNation.enabled_objects

        self.fields['category'].choices = models.Category.get_choices()


class CaseModelForm(forms.ModelForm):
    js_file = 'js/case_form.js'

    class Meta:
        model = models.Case
        fields = ['name', 'archive_no', 'closed', 'client', 'owner',
                  'category', 'stage', 'trademark', 'desc']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['client'].queryset = base_models.Client.enabled_objects
        self.fields['owner'].queryset = base_models.Owner.enabled_objects
        # self.fields['category'].queryset = models.Category.enabled_objects
        self.fields['stage'].queryset = models.Stage.enabled_objects

        self.fields['category'].choices = models.Category.get_choices()

    def _post_clean(self):
        """
        根据instance的category设置trademark或者pattern
        因为希望操作instance的category/trademark/pattern属性，
        所以把这个逻辑放在_post_clean()中，
        而不是clean()中
        """
        super()._post_clean()
        if self.instance.category.parent_id == 2:
            # 当category属于pattern
            self.instance.trademark = None
        elif self.instance.category.parent_id == 1:
            # 当category属于trademark
            pass
