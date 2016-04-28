# -*- coding: utf-8 -*-
from django.conf.urls import url, include
from django.conf.urls.static import static
from django.contrib import admin
from django.conf import settings
from . import views

urlpatterns = [
    url(r'^'+settings.SUBDIRECTORY+'$', views.index, name='index'),
    url(r'^'+settings.SUBDIRECTORY+'denied$', views.denied, name='denied'),
    url(r'^'+settings.SUBDIRECTORY+'admin/', admin.site.urls, name='admin'),
    url(r'^'+settings.SUBDIRECTORY+'logout', views.logout, name='auth_logout'),
    url(r'^'+settings.SUBDIRECTORY+'skoli/', include('schools.urls')),
    url(r'^'+settings.SUBDIRECTORY+'skoli/', include('supportandexception.urls')),
]
