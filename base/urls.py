# -*- coding: utf-8 -*-

from django.conf.urls import url
from django.contrib.auth import views as auth_views
from . import views

app_name = 'base'

urlpatterns = [
    url(r'^$', views.IndexView.as_view(), name='index'),
    url(r'^login/$', auth_views.LoginView.as_view(), name='login'),
    url(r'^logout/$', auth_views.LogoutView.as_view(), name='logout'),
    url(r'^client/$', views.ClientListView.as_view(), name='client_list'),
]