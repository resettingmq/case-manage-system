# -*- coding: utf-8 -*-

from django import forms

from . import models


class ClientModelForm(forms.ModelForm):
    class Meta:
        model = models.Client
        fields = ['name', 'is_agent', 'tel', 'mobile', 'fax', 'state', 'city',
                  'address', 'postal_code', 'currency', 'country', 'desc']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['currency'].queryset = models.Currency.enabled_objects
        self.fields['country'].queryset = models.Country.enabled_objects
