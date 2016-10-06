# -*- coding: utf-8 -*-
from django.conf.urls import url

from .views import *

app_name = 'samraemd'
urlpatterns = [
	url(r'^stæ/$', SamraemdMathResultAdminListing.as_view(), name='math_admin_listing'),
	url(r'^stæ/(?P<school_id>\d+)/$', SamraemdMathResultListing.as_view(), name='math_listing'),
	url(r'^stæ/(?P<exam_code>[\w ]+)/$', SamraemdMathResultDetail.as_view(), name='math_detail'),
	url(r'^stæ/(?P<school_id>\d+)/(?P<exam_code>[\w ]+)/$', SamraemdMathResultDetail.as_view(), name='math_detail'),
	url(r'^stæ/niðurstöður/create/$', SamraemdMathResultCreate.as_view(), name='math_create'),
	url(r'^stæ/niðurstöður/(?P<exam_code>[\w ]+)/delete/$', SamraemdMathResultDelete.as_view(), name='math_delete'),
	url(r'^isl/$', SamraemdISLResultAdminListing.as_view(), name='isl_admin_listing'),
	url(r'^isl/(?P<school_id>\d+)/$', SamraemdISLResultListing.as_view(), name='isl_listing'),
	url(r'^isl/(?P<exam_code>[\w ]+)/$', SamraemdISLResultDetail.as_view(), name='isl_detail'),
	url(r'^isl/(?P<school_id>\d+)/(?P<exam_code>[\w ]+)/$', SamraemdISLResultDetail.as_view(), name='isl_detail'),
	url(r'^isl/niðurstöður/create/$', SamraemdISLResultCreate.as_view(), name='isl_create'),
	url(r'^isl/niðurstöður/(?P<exam_code>[\w ]+)/delete/$', SamraemdISLResultDelete.as_view(), name='isl_delete'),
]