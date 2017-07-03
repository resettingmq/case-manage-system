# -*- coding: utf-8 -*-

from django.conf.urls import url
from django.contrib.auth import views as auth_views
from . import views

app_name = 'base'

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^login/$', auth_views.LoginView.as_view(), name='login'),
    url(r'^logout/$', auth_views.LogoutView.as_view(), name='logout'),
]