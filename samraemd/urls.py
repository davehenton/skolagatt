# -*- coding: utf-8 -*-
from django.conf.urls import url

from samraemd import views

app_name = 'samraemd'
urlpatterns = [
    # Results for school managers
    # General results
    url(r'^niðurstöður/(?P<school_id>\d+)$',
        views.SamraemdResultListing.as_view(),
        name='result_list'),
    url(r'^niðurstöður/(?P<school_id>\d+)/bekkur/(?P<studentgroup_id>\d+)/$',
        views.SamraemdStudentGroupResultListing.as_view(),
        name='result_list_studentgroup'),
    url(r'^niðurstöður/(?P<school_id>\d+)/(?P<year>\d+)/(?P<group>\d+)$',
        views.SamraemdResultDetail.as_view(),
        name='result_detail'),
    url(r'^niðurstöður/(?P<school_id>\d+)/(?P<year>\d+)/(?P<group>\d+)/excel/$',
        views.excel_result,
        name='result_excel'),
    url(r'^niðurstöður/(?P<school_id>\d+)/(?P<year>\d+)/(?P<group>\d+)/einkunnablod/$',
        views.SamraemdResultDetail.as_view(),
        name='result_print'),
    url(r'^niðurstöður/(?P<school_id>\d+)/(?P<year>\d+)/(?P<group>\d+)/(?P<student_id>\d+)/einkunnablod/$',
        views.SamraemdResultDetail.as_view(),
        name='result_single_print'),
    url(r'^niðurstöður/(?P<school_id>\d+)/(?P<year>\d+)/(?P<group>\d+)/hrágögn/$',
        views.SamraemdRawResultDetail.as_view(),
        name='result_detail_raw'),
    url(r'^niðurstöður/(?P<school_id>\d+)/(?P<year>\d+)/(?P<group>\d+)/hrágögn/einkunnablod/$',
        views.SamraemdRawResultDetail.as_view(),
        name='result_raw_print'),
    url(r'^niðurstöður/(?P<school_id>\d+)/(?P<year>\d+)/(?P<group>\d+)/(?P<student_id>\d+)/(?P<exam_code>[\w ]+)/hrágögn/einkunnablod/$',
        views.SamraemdRawResultDetail.as_view(),
        name='result_raw_single_print'),
    url(r'^niðurstöður/rawdata/$',
        views.RawDataCreate.as_view(),
        name='rawdatacreate'),
    url(r'^niðurstöður/$',
        views.SamraemdResultAdminListing.as_view(),
        name='result_admin_listing'),
    url(r'^niðurstöður/create/$',
        views.SamraemdResultCreate.as_view(),
        name="result_create"),

    # Math results
    url(r'^stæ/(?P<school_id>\d+)/$',
        views.SamraemdMathResultListing.as_view(),
        name='math_listing'),
    url(r'^stæ/niðurstöður/(?P<exam_code>[\w ]+)/delete/$',
        views.SamraemdMathResultDelete.as_view(),
        name='math_delete'),

    # Icelandic results
    url(r'^isl/(?P<school_id>\d+)/$',
        views.SamraemdISLResultListing.as_view(),
        name='isl_listing'),
    url(r'^isl/niðurstöður/(?P<exam_code>[\w ]+)/delete/$',
        views.SamraemdISLResultDelete.as_view(),
        name='isl_delete'),

    # English results
    url(r'^ens/(?P<school_id>\d+)/$',
        views.SamraemdENSResultListing.as_view(),
        name='ens_listing'),
    url(r'^ens/niðurstöður/(?P<exam_code>[\w ]+)/delete/$',
        views.SamraemdENSResultDelete.as_view(),
        name='ens_delete'),

    # Results for Admins
    # General results
    url(r'^niðurstöður/(?P<year>\d+)/(?P<group>\d+)/einkunnablod/$',
        views.SamraemdResultDetail.as_view(),
        name='admin_result_print'),
    url(r'^niðurstöður/(?P<school_id>\d+)/(?P<year>\d+)/(?P<group>\d+)/hrá/excel/$',
        views.excel_result_raw,
        name='result_raw_excel'),
    url(r'^niðurstöður/(?P<exam_code>[\w ]+)/(?P<year>\d+)/(?P<group>\d+)/delete/$',
        views.SamraemdResultDelete.as_view(),
        name='raw_delete'),

    # Math an ISL results
    url(r'^umsjónarmaður/stæ/niðurstöður/(?P<year>\d+)/(?P<group>\d+)$',
        views.SamraemdResultDetail.as_view(),
        name='math_admin_result_detail'),
    url(r'^umsjónarmaður/isl/niðurstöður/(?P<year>\d+)/(?P<group>\d+)$',
        views.SamraemdResultDetail.as_view(),
        name='isl_admin_result_detail'),
    url(r'^umsjónarmaður/ens/niðurstöður/(?P<year>\d+)/(?P<group>\d+)$',
        views.SamraemdResultDetail.as_view(),
        name='ens_admin_result_detail'),
    url(r'^umsjónarmaður/niðurstöður/(?P<exam_code>\w+)/(?P<year>\d+)/(?P<group>\d+)$',
        views.SamraemdRawResultDetail.as_view(),
        name='admin_result_detail'),
    url(r'^umsjónarmaður/niðurstöður/(?P<exam_code>\w+)/(?P<year>\d+)/(?P<group>\d+)/rawexcel/$',
        views.admin_result_raw_excel,
        name='admin_result_raw_excel'),
    url(r'^umsjónarmaður/niðurstöður/(?P<exam_code>\w+)/(?P<year>\d+)/(?P<group>\d+)/einkunnablod/$',
        views.SamraemdRawResultDetail.as_view(),
        name='admin_result_raw_print'),
]
