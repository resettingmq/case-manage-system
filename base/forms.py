# -*- coding: utf-8 -*-

from django import forms
from django.core.exceptions import ValidationError

from . import models


class ClientModelForm(forms.ModelForm):
    class Meta:
        model = models.Client
        fields = ['name', 'is_agent', 'tel', 'mobile', 'fax', 'email', 'state', 'city',
                  'address', 'postal_code', 'currency', 'country', 'desc']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['currency'].queryset = models.Currency.enabled_objects
        self.fields['country'].queryset = models.Country.enabled_objects


class TrademarkModelForm(forms.ModelForm):
    class Meta:
        model = models.Trademark
        fields = ['name', 'client', 'desc']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['client'].queryset = models.Client.enabled_objects


class TrademarkNationModelForm(forms.ModelForm):
    class Meta:
        model = models.TrademarkNation
        fields = ['trademark', 'country',
                  'app_no', 'app_date', 'applicant',
                  'register_no', 'register_date', 'state', 'desc']
        widgets = {
            'app_date': forms.TextInput(attrs={
                'data-provide': 'datepicker',
                'data-date-format': 'yyyy-mm-dd',
            }),
            'register_date': forms.TextInput(attrs={
                'data-provide': 'datepicker',
                'data-date-format': 'yyyy-mm-dd',
            }),
        }

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.fields['trademark'].queryset = models.Trademark.enabled_objects
            self.fields['country'].queryset = models.Country.enabled_objects

    def clean(self):
        cleaned_data = super().clean()
        if models.TrademarkNation.enabled_objects.filter(
            trademark_id=cleaned_data['trademark'],
            country_id=cleaned_data['country']
        ).exists():
            raise ValidationError('该商标-进入国家已经存在')
        return cleaned_data


class TrademarkNationNiceModelForm(forms.ModelForm):
    class Meta:
        model = models.TrademarkNationNice
        # 注意，form中没有trademarknation field
        # RelatedEntityView会自动把main_object关联到self.object上
        fields = ['nice_class', 'goods']
