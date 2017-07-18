# -*- coding: utf-8 -*-

from django.conf.urls import url
from . import views

app_name = 'case'

urlpatterns = [
    url(r'^$', views.CaseListView.as_view(), name='case_list'),
    url(r'^(?P<case_id>\d+)/$', views.CaseRelatedEntityView.as_view(), name='case_detail'),
    url(r'^create/$', views.CaseCreateView.as_view(), name='case_create'),
]
