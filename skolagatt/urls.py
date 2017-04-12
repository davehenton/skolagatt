# -*- coding: utf-8 -*-
from django.conf.urls import url, include
from django.contrib import admin
from . import views

urlpatterns = [
    url(r'^$',
        views.index,
        name='index'),
    url(r'^denied$',
        views.denied,
        name='denied'),
    url(r'^admin/',
        admin.site.urls,
        name='admin'),
    url(r'^accounts/login',
        views.login,
        name='auth_login'),
    url(r'^accounts/logout',
        views.logout,
        name='auth_logout'),
    url(r'^skoli/',
        include('schools.urls')),
    url(r'^stuðningur/',
        include('supportandexception.urls')),
    url(r'^samræmd/',
        include('samraemd.urls')),
    url(r'^profagrunnur/',
        include('survey.urls')),
    url(r'^froala_editor/', include('froala_editor.urls')),
    url(r'^images$', views.images, name='images'),
]
