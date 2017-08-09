# -*- coding: utf-8 -*-

from django.conf.urls import url, include

from . import views

income_urlpatterns = [
    url(r'^$', views.IncomeListView.as_view(), name='list'),
    url(r'^(?P<income_id>\d+)/$', views.IncomeRelatedEntityView.as_view(), name='detail'),
    url(r'^create/$', views.IncomeCreateView.as_view(), name='create'),
    url(r'^disable/(?P<income_id>\d+)/$', views.IncomeDisableView.as_view(), name='disable'),
]

urlpatterns = [
    url(r'^income/', include(income_urlpatterns, namespace='income')),
]