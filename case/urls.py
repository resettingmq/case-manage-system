# -*- coding: utf-8 -*-

from django.conf.urls import url, include
from . import views

case_urlpatterns = [
    url(r'^$', views.CaseListView.as_view(), name='list'),
    url(r'^(?P<case_id>\d+)/$', views.CaseRelatedEntityView.as_view(), name='detail'),
    url(r'^create/$', views.CaseCreateView.as_view(), name='create'),
]

subcase_urlpatterns = [
    url(r'^$', views.SubCaseListView.as_view(), name='list'),
    url(r'^(?P<subcase_id>\d+)/$', views.SubCaseRelatedEntityView.as_view(), name='detail'),
    url(r'^create/$', views.SubCaseCreateView.as_view(), name='create')
]

urlpatterns = [
    url(r'^case/', include(case_urlpatterns, namespace='case')),
    url(r'^subcase/', include(subcase_urlpatterns, namespace='subcase')),
]
