# -*- coding: utf-8 -*-

from django.conf.urls import url, include
from django.contrib.auth import views as auth_views
from . import views

app_name = 'base'

client_urlpatterns = [
    url(r'^$', views.ClientListView.as_view(), name='client_list'),
    url(r'^(?P<client_id>\d+)/$', views.ClientDetailView.as_view(), name='client_detail'),
    url(r'^create/$', views.ClientCreateView.as_view(), name='client_create'),
]

urlpatterns = [
    url(r'^$', views.IndexView.as_view(), name='index'),
    url(r'^login/$', auth_views.LoginView.as_view(), name='login'),
    url(r'^logout/$', auth_views.LogoutView.as_view(), name='logout'),
    url(r'^client/', include(client_urlpatterns)),
]
