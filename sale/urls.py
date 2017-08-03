# -*- coding: utf-8 -*-

from django.conf.urls import url, include

from . import views

receivable_urlpatterns = [
    url(r'^$', views.ReceivableListView.as_view(), name='list'),
    url(r'^(?P<receivable_id>\d+)/$', views.ReceivableRelatedEntityView.as_view(), name='detail'),
    url(r'^create/$', views.ReceivableCreateView.as_view(), name='create'),
    url(r'^disable/(?P<receivable_id>\d+)/$', views.ReceivableDisableView.as_view(), name='disable'),
]

receipts_urlpatterns = [
    url(r'^$', views.ReceiptsListView.as_view(), name='list'),
    url(r'^(?P<receipts_id>\d+)/$', views.ReceiptsRelatedEntityView.as_view(), name='detail'),
    url(r'^create/$', views.ReceiptsCreateView.as_view(), name='create'),
    url(r'^disable/(?P<receipts_id>\d+)/$', views.ReceiptsDisableView.as_view(), name='disable'),
]

urlpatterns = [
    url(r'^receivable/', include(receivable_urlpatterns, namespace='receivable')),
    url(r'^receipts/', include(receipts_urlpatterns, namespace='receipts')),
]
