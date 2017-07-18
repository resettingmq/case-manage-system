# -*- coding: utf-8 -*-

from django.conf.urls import url
from . import views

app_name = 'case'

urlpatterns = [
    url(r'^$', views.CaseListView.as_view(), name='case_list'),
]
