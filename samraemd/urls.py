# -*- coding: utf-8 -*-
from django.conf.urls import url

from .views import *

app_name = 'samraemd'
urlpatterns = [
	url(r'^niðurstöður/(?P<school_id>\d+)$', SamraemdResultListing.as_view(), name='result_list'),
	url(r'^niðurstöður/(?P<school_id>\d+)/(?P<year>\d+)/(?P<group>\d+)$', SamraemdResultDetail.as_view(), name='result_detail'),
	url(r'^niðurstöður/(?P<school_id>\d+)/(?P<year>\d+)/(?P<group>\d+)/einkunnablod/$', SamraemdResultDetail.as_view(), name='result_print'),
	url(r'^niðurstöður/(?P<year>\d+)/(?P<group>\d+)/einkunnablod/$', SamraemdResultDetail.as_view(), name='admin_result_print'),
	url(r'^niðurstöður/(?P<school_id>\d+)/(?P<year>\d+)/(?P<group>\d+)/csv_isl/$', result_csv_isl, name='result_csv_isl'),
	url(r'^niðurstöður/(?P<school_id>\d+)/(?P<year>\d+)/(?P<group>\d+)/csv_stf/$', result_csv_stf, name='result_csv_stf'),
	url(r'^stæ/$', SamraemdMathResultAdminListing.as_view(), name='math_admin_listing'),
	url(r'^stæ/(?P<school_id>\d+)/$', SamraemdMathResultListing.as_view(), name='math_listing'),
	url(r'^stæ/niðurstöður/create/$', SamraemdMathResultCreate.as_view(), name='math_create'),
	url(r'^stæ/niðurstöður/(?P<exam_code>[\w ]+)/delete/$', SamraemdMathResultDelete.as_view(), name='math_delete'),
	url(r'^isl/$', SamraemdISLResultAdminListing.as_view(), name='isl_admin_listing'),
	url(r'^isl/(?P<school_id>\d+)/$', SamraemdISLResultListing.as_view(), name='isl_listing'),
	url(r'^isl/niðurstöður/create/$', SamraemdISLResultCreate.as_view(), name='isl_create'),
	url(r'^isl/niðurstöður/(?P<exam_code>[\w ]+)/delete/$', SamraemdISLResultDelete.as_view(), name='isl_delete'),
	url(r'^umsjónarmaður/stæ/niðurstöður/(?P<year>\d+)/(?P<group>\d+)$', SamraemdResultDetail.as_view(), name='math_admin_result_detail'),
	url(r'^umsjónarmaður/isl/niðurstöður/(?P<year>\d+)/(?P<group>\d+)$', SamraemdResultDetail.as_view(), name='isl_admin_result_detail'),
	url(r'^umsjónarmaður/niðurstöður/(?P<year>\d+)/(?P<group>\d+)/csv/$', admin_result_csv_isl, name='admin_result_csv_isl'),
	url(r'^umsjónarmaður/niðurstöður/(?P<year>\d+)/(?P<group>\d+)/csv/$', admin_result_csv_stf, name='admin_result_csv_stf'),
]