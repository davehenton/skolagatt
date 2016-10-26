# -*- coding: utf-8 -*-
from django.conf.urls import url

from .views import *
from .api import SchoolViewSet

app_name = 'schools'
urlpatterns = [
    url(r'^$', SchoolListing.as_view(), name='school_listing'),
    url(r'^api$', SchoolViewSet.as_view({'get': 'list'}), name='api_school_listing'),
    url(r'^(?P<pk>\d+)/$', SchoolDetail.as_view(), name='school_detail'),
    url(r'^create/$', SchoolCreate.as_view(), name='school_create'),
    url(r'^create/import$', SchoolCreateImport.as_view(), name='school_create_import'),
    url(r'^(?P<pk>\d+)/update/$', SchoolUpdate.as_view(), name='school_update'),
    url(r'^(?P<pk>\d+)/delete/$', SchoolDelete.as_view(), name='school_delete'),

    url(r'^notification/create/$', NotificationCreate.as_view(), name='notification_create'),

    url(r'^(?P<school_id>\d+)/lesferill/$', lesferill, name='lesferill'),

    url(r'^(?P<school_id>\d+)/nemandi/$', StudentListing.as_view(), name='student_listing'),
    url(r'^(?P<school_id>\d+)/nemandi/(?P<pk>\d+)/$', StudentDetail.as_view(), name='student_detail'),
    url(r'^(?P<school_id>\d+)/nemandi/(?P<pk>\d+)/notes_save/$', StudentNotes, name='notes_save'),
    url(r'^(?P<school_id>\d+)/nemandi/create/$', StudentCreate.as_view(), name='student_create'),
    url(r'^(?P<school_id>\d+)/nemandi/create/import$', StudentCreateImport.as_view(), name='student_create_import'),
    url(r'^(?P<school_id>\d+)/nemandi/(?P<pk>\d+)/update/$', StudentUpdate.as_view(), name='student_update'),
    url(r'^(?P<school_id>\d+)/nemandi/(?P<pk>\d+)/delete/$', StudentDelete.as_view(), name='student_delete'),

    url(r'^(?P<school_id>\d+)/nemandi/(?P<student_id>\d+)/próf/(?P<survey_id>\d+)/niðurstöður/create/$', SurveyResultCreate.as_view(), name='survey_result_create'),
    url(r'^(?P<school_id>\d+)/nemandi/(?P<student_id>\d+)/próf/(?P<survey_id>\d+)/niðurstöður/(?P<pk>\d+)/update/$', SurveyResultUpdate.as_view(), name='survey_result_update'),
    url(r'^(?P<school_id>\d+)/nemandi/(?P<student_id>\d+)/próf/(?P<survey_id>\d+)/niðurstöður/(?P<pk>\d+)/delete/$', SurveyResultDelete.as_view(), name='survey_result_delete'),

    url(r'^(?P<school_id>\d+)/bekkur/$', StudentGroupListing.as_view(), name='group_listing'),
    url(r'^(?P<school_id>\d+)/bekkur/(?P<pk>\d+)/$', StudentGroupDetail.as_view(), name='group_detail'),
    url(r'^(?P<school_id>\d+)/bekkur/create/$', StudentGroupCreate.as_view(), name='group_create'),
    url(r'^(?P<school_id>\d+)/bekkur/(?P<pk>\d+)/update/$', StudentGroupUpdate.as_view(), name='group_update'),
    url(r'^(?P<school_id>\d+)/bekkur/(?P<pk>\d+)/delete/$', StudentGroupDelete.as_view(), name='group_delete'),
    url(r'^(?P<school_id>\d+)/bekkur/(?P<student_group>\d+)/próf/create/$', SurveyCreate.as_view(), name='survey_create'),

    url(r'^(?P<school_id>\d+)/skolastjórn/$', ManagerListing.as_view(), name='manager_listing'),
    url(r'^skolastjórn/(?P<pk>\d+)/$', ManagerOverview.as_view(), name='manager_overview'),
    url(r'^(?P<school_id>\d+)/skolastjórn/(?P<pk>\d+)/$', ManagerDetail.as_view(), name='manager_detail'),
    url(r'^(?P<school_id>\d+)/skolastjórn/create/$', ManagerCreate.as_view(), name='manager_create'),
    url(r'^skolastjórn/create/import$', ManagerCreateImport.as_view(), name='manager_create_import'),
    url(r'^(?P<school_id>\d+)/skolastjórn/(?P<pk>\d+)/update/$', ManagerUpdate.as_view(), name='manager_update'),
    url(r'^(?P<school_id>\d+)/skolastjórn/(?P<pk>\d+)/delete/$', ManagerDelete.as_view(), name='manager_delete'),

    url(r'^(?P<school_id>\d+)/kennari/$', TeacherListing.as_view(), name='teacher_listing'),
    url(r'^kennari/(?P<pk>\d+)/$', TeacherOverview.as_view(), name='teacher_overview'),
    url(r'^(?P<school_id>\d+)/kennari/(?P<pk>\d+)/$', TeacherDetail.as_view(), name='teacher_detail'),
    url(r'^(?P<school_id>\d+)/kennari/create/$', TeacherCreate.as_view(), name='teacher_create'),
    url(r'^(?P<school_id>\d+)/kennari/create/import$', TeacherCreateImport.as_view(), name='teacher_create_import'),
    url(r'^(?P<school_id>\d+)/kennari/(?P<pk>\d+)/update/$', TeacherUpdate.as_view(), name='teacher_update'),
    url(r'^(?P<school_id>\d+)/kennari/(?P<pk>\d+)/delete/$', TeacherDelete.as_view(), name='teacher_delete'),

    url(r'^(?P<school_id>\d+)/próf/$', SurveyListing.as_view(), name='survey_listing'),
    url(r'^(?P<school_id>\d+)/próf/(?P<pk>\d+)/$', SurveyDetail.as_view(), name='survey_detail'),
    url(r'^(?P<school_id>\d+)/próf/(?P<pk>\d+)/update/$', SurveyUpdate.as_view(), name='survey_update'),
    url(r'^(?P<school_id>\d+)/próf/(?P<pk>\d+)/delete/$', SurveyDelete.as_view(), name='survey_delete'),

    url(r'^lykilorð/$', SurveyLoginAdminListing.as_view(), name='survey_login_admin_listing'),
    url(r'^lykilorð/(?P<survey_id>[\w ]+)$', SurveyLoginDetail.as_view(), name='survey_login_detail_all'),
    url(r'^lykilorð/(?P<survey_id>[\w ]+)/(?P<print>[\w ]+)/$', SurveyLoginDetail.as_view(), name='surveylogin_detail_print'),
    url(r'^(?P<school_id>\d+)/lykilorð/$', SurveyLoginListing.as_view(), name='survey_login_listing'),
    url(r'^(?P<school_id>\d+)/lykilorð/(?P<survey_id>[\w ]+)$', SurveyLoginDetail.as_view(), name='survey_login_detail'),
    url(r'^(?P<school_id>\d+)/lykilorð/(?P<survey_id>[\w ]+)/(?P<print>[\w ]+)/$', SurveyLoginDetail.as_view(), name='surveylogin_detail_print'),
    url(r'^próf/create$', SurveyLoginCreate.as_view(), name='survey_login_create'),
    url(r'^próf/(?P<survey_id>[\w ]+)/delete/$', SurveyLoginDelete.as_view(), name='surveylogin_delete'),

    url(r'^umsjónarmenn/$', AdminListing.as_view(), name='admin_listing'),
    url(r'^umsjónarmenn/create$', AdminCreate.as_view(), name='admin_create'),
    url(r'^umsjónarmenn/(?P<pk>\d+)/update/$', AdminUpdate.as_view(), name='admin_update'),
    url(r'^umsjónarmenn/próf/$', SurveyAdminListing.as_view(), name='survey_admin_listing'),
    url(r'^umsjónarmenn/próf/(?P<survey_title>[^\/]*)/$', StudentGroupAdminListing.as_view(), name='group_admin_listing'),
    url(r'^umsjónarmenn/próf/(?P<survey_title>[^\/]*)/csv/$', group_admin_listing_csv, name='group_admin_listing_csv'),
    url(r'^umsjónarmenn/próf/(?P<survey_title>[^\/]*)/Excel/$', group_admin_listing_excel, name='group_admin_listing_excel'),
    url(r'^umsjónarmenn/próf/(?P<survey_title>[^\/]*)/Excel-Mæting/$', group_admin_attendance_excel, name='group_admin_attendance_excel'),

]