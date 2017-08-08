# -*- coding: utf-8 -*-

from django.conf.urls import url, include

from . import views

expense_urlpatterns = [
    url(r'^$', views.ExpenseListView.as_view(), name='list'),
    url(r'^(?P<expense_id>\d+)/$', views.ExpenseRelatedEntityView.as_view(), name='detail'),
    url(r'^create/$', views.ExpenseCreateView.as_view(), name='create'),
    url(r'^disable/(?P<expense_id>\d+)/$', views.ExpenseDisableView.as_view(), name='disable'),
]

urlpatterns = [
    url(r'^expense/', include(expense_urlpatterns, namespace='expense')),
]
