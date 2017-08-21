# -*- coding: utf-8 -*-

from django.conf.urls import url, include
from django.contrib.auth import views as auth_views
from . import views

client_urlpatterns = [
    url(r'^$', views.ClientListView.as_view(), name='list'),
    url(r'^(?P<client_id>\d+)/$', views.ClientRelatedEntityView.as_view(), name='detail'),
    url(r'^create/$', views.ClientCreateView.as_view(), name='create'),
    url(r'^disable/(?P<client_id>\d+)/$', views.ClientDisableView.as_view(), name='disable')
]

trademark_urlpatterns = [
    url(r'^$', views.TrademarkListView.as_view(), name='list'),
    url(r'^(?P<trademark_id>\d+)/$', views.TrademarkRelatedEntityView.as_view(), name='detail'),
    url(r'^create/$', views.TrademarkCreateView.as_view(), name='create'),
    url(r'^disable/(?P<trademark_id>\d+)/$', views.TrademarkDisableView.as_view(), name='disable'),
]

trademarknation_urlpatterns = [
    url(r'^$', views.TrademarkNationListView.as_view(), name='list'),
    url(r'^(?P<trademarknation_id>\d+)/$', views.TrademarkNationRelatedEntityView.as_view(), name='detail'),
    url(r'^create/$', views.TrademarkNationCreateView.as_view(), name='create'),
    url(r'^disable/(?P<trademarknation_id>\d+)/$', views.TrademarkNationDisableView.as_view(), name='disable'),
]

trademarknationnice_urlpatterns = [
    url(
        r'^(?P<trademarknationnice_id>\d+)/$',
        views.TrademarkNationNiceRelatedEntityView.as_view(),
        name='detail'
    ),
    url(
        r'^disable/(?P<trademarknationnice_id>\d+)/$',
        views.TrademarkNationNiceDisableView.as_view(),
        name='disable'
    ),
]

pattern_urlpatterns = [
    url(r'^$', views.PatternListView.as_view(), name='list'),
    url(r'^(?P<pattern_id>\d+)/$', views.PatternRelatedEntityView.as_view(), name='detail'),
    url(r'^create/$', views.PatternCreateView.as_view(), name='create'),
    url(r'^disable/(?P<pattern_id>\d+)/$', views.PatternDisableView.as_view(), name='disable'),
]

patternnation_urlpatterns = [
    url(r'^$', views.PatternNationListView.as_view(), name='list'),
    url(r'^(?P<patternnation_id>\d+)/$', views.PatternNationRelatedEntityView.as_view(), name='detail'),
    url(r'^create/$', views.PatternNationCreateView.as_view(), name='create'),
    url(r'^disable/(?P<patternnation_id>\d+)/$', views.PatternNationDisableView.as_view(), name='disable'),
]

urlpatterns = [
    url(r'^$', views.IndexView.as_view(), name='index'),
    url(r'^login/$', auth_views.LoginView.as_view(), name='login'),
    url(r'^logout/$', auth_views.LogoutView.as_view(), name='logout'),
    url(r'^client/', include(client_urlpatterns, namespace='client')),
    url(r'^trademark/', include(trademark_urlpatterns, namespace='trademark')),
    url(r'^trademark/nation/', include(trademarknation_urlpatterns, namespace='trademarknation')),
    url(r'^trademark/nation/nice/', include(
        trademarknationnice_urlpatterns, namespace='trademarknationnice'
    )),
    url(r'^pattern/', include(pattern_urlpatterns, namespace='pattern')),
    url(r'^pattern/nation/', include(patternnation_urlpatterns, namespace='patternnation'))
]
