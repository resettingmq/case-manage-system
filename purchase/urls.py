# -*- coding: utf-8 -*-

from django.conf.urls import url, include

from . import views

payable_urlpatterns = [
    url(r'^$', views.PayableListView.as_view(), name='list'),
    url(r'^(?P<payable_id>\d+)/$', views.PayableRelatedEntityView.as_view(), name='detail'),
    url(r'^create/$', views.PayableCreateView.as_view(), name='create'),
    url(r'^disable/(?P<payable_id>\d+)/$', views.PayableDisableView.as_view(), name='disable'),
]

payment_urlpatterns = [
    url(r'^$', views.PaymentListView.as_view(), name='list'),
    url(r'^(?P<payment_id>\d+)/$', views.PaymentRelatedEntityView.as_view(), name='detail'),
    url(r'^create/$', views.PaymentCreateView.as_view(), name='create'),
    url(r'^disable/(?P<payment_id>\d+)/$', views.PaymentDisableView.as_view(), name='disable'),
]

urlpatterns = [
    url(r'^payable/', include(payable_urlpatterns, namespace='payable')),
    url(r'^payment/', include(payment_urlpatterns, namespace='payment')),
]
