# -*- coding: utf-8 -*-

from django import forms
from django.core.exceptions import ValidationError

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
    js_file = 'js/subcase_form.js'
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
                  'category', 'stage', 'trademarknation', 'patternnation',
                  'closed', 'desc']

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
        self.fields['patternnation'].queryset = base_models.PatternNation.enabled_objects

        self.fields['category'].choices = models.Category.get_choices()

    def _post_clean(self):
        """
        根据instance的category设置trademarknation或者patternnation
        因为希望操作instance的category/trademarknation/patternnation属性，
        所以把这个逻辑放在_post_clean()中，
        而不是clean()中
        同时在判断相关专利/商标是否为空时，
        应该直接调用self.add_error()增加ValidationError实例
        而不是直接raise
        因为Django form的实现中，并没有捕获_post_clean()抛出异常的逻辑
        所以需要在_post_clean()中手动将ValidationError添加到form.errors中
        """
        super()._post_clean()
        # todo: 增加与case完整性验证
        if self.instance.category.parent_id == 2:
            # 当category属于pattern
            if self.instance.patternnation is None:
                # 判断专利是否为空
                self.add_error(None, ValidationError('当分案分类属于专利时，必须为该分案指定与之相关联的专利-进入国家'))
                return
            if self.instance.case.pattern_id != self.instance.patternnation.pattern_id:
                # 验证case, patternnation之间的关系
                self.add_error(None, ValidationError('所属案件与专利-进入国家必须关联于同一个专利'))
                return
            self.instance.trademarknation = None
        elif self.instance.category.parent_id == 1:
            # 当category属于trademark
            if self.instance.trademarknation is None:
                # 判断商标是否为空
                self.add_error(None, ValidationError('当分案件类属于商标时，必须为该分案指定与之相关联的商标-进入国家'))
                return
            if self.instance.case.trademark_id != self.instance.trademarknation.trademark_id:
                # 验证case, trademarknation之间的关系
                self.add_error(None, ValidationError('所属案件与商标-进入国家必须关联于同一个商标'))
                return
            self.instance.patternnation = None


class CaseModelForm(forms.ModelForm):
    js_file = 'js/case_form.js'

    class Meta:
        model = models.Case
        fields = ['name', 'archive_no', 'closed', 'owner',
                  'category', 'stage', 'trademark', 'pattern', 'desc']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['owner'].queryset = base_models.Owner.enabled_objects
        # self.fields['category'].queryset = models.Category.enabled_objects
        self.fields['stage'].queryset = models.Stage.enabled_objects
        self.fields['trademark'].queryset = base_models.Trademark.enabled_objects
        self.fields['pattern'].queryset = base_models.Pattern.enabled_objects

        self.fields['category'].choices = models.Category.get_choices()

    def _post_clean(self):
        """
        根据instance的category设置trademark或者pattern
        因为希望操作instance的category/trademark/pattern属性，
        所以把这个逻辑放在_post_clean()中，
        而不是clean()中
        同时在判断相关专利/商标是否为空时，
        应该直接调用self.add_error()增加ValidationError实例
        而不是直接raise
        因为Django form的实现中，并没有捕获_post_clean()抛出异常的逻辑
        所以需要在_post_clean()中手动将ValidationError添加到form.errors中
        """
        super()._post_clean()
        if self.instance.category.parent_id == 2:
            # 当category属于pattern
            if self.instance.pattern is None:
                # 判断专利是否为空
                self.add_error(None, ValidationError('当案件分类属于专利时，必须为该案件指定与之相关联的专利'))
                return
            # 保证一个case中，trademark和pattern有且只有一个会被设置
            self.instance.trademark = None
            # 保存case.client信息
            self.instance.client_id = self.instance.pattern.client_id
        elif self.instance.category.parent_id == 1:
            # 当category属于trademark
            if self.instance.trademark is None:
                # 判断商标是否为空
                self.add_error(None, ValidationError('当案件分类属于商标时，必须为该案件指定与之相关联的商标'))
                return
            # 保证一个case中，trademark和pattern有且只有一个会被设置
            self.instance.pattern = None
            # 保存case.client信息
            self.instance.client_id = self.instance.trademark.client_id
