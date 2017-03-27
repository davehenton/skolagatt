# -*- coding: utf-8 -*-
from django.conf.urls import url

import schools.views as views
from .api import SchoolViewSet

app_name = 'schools'
urlpatterns = [
    url(r'^$',
        views.SchoolListing.as_view(),
        name='school_listing'),
    url(r'^api$',
        SchoolViewSet.as_view({'get': 'list'}),
        name='api_school_listing'),
    url(r'^(?P<pk>\d+)/$',
        views.SchoolDetail.as_view(),
        name='school_detail'),
    url(r'^(?P<pk>\d+)/lesfimi_excel/$',
        views.lesfimi_excel_for_principals,
        name='lesfimi_excel_for_principals'),
    url(r'^create/$',
        views.SchoolCreate.as_view(),
        name='school_create'),
    url(r'^create/import$',
        views.SchoolCreateImport.as_view(),
        name='school_create_import'),
    url(r'^(?P<pk>\d+)/update/$',
        views.SchoolUpdate.as_view(),
        name='school_update'),
    url(r'^(?P<pk>\d+)/delete/$',
        views.SchoolDelete.as_view(),
        name='school_delete'),

    url(r'^notification/create/$',
        views.NotificationCreate.as_view(),
        name='notification_create'),

    url(r'^lesferill/$',
        views.lesferill,
        name='lesferill'),

    url(r'^(?P<school_id>\d+)/nemandi/$',
        views.StudentListing.as_view(),
        name='student_listing'),
    url(r'^(?P<school_id>\d+)/nemandi/(?P<pk>\d+)/$',
        views.StudentDetail.as_view(),
        name='student_detail'),
    url(r'^(?P<school_id>\d+)/nemandi/(?P<pk>\d+)/notes_save/$',
        views.StudentNotes,
        name='notes_save'),
    url(r'^(?P<school_id>\d+)/nemandi/create/$',
        views.StudentCreate.as_view(),
        name='student_create'),
    url(r'^(?P<school_id>\d+)/nemandi/create/import$',
        views.StudentCreateImport.as_view(),
        name='student_create_import'),
    url(r'^(?P<school_id>\d+)/nemandi/(?P<pk>\d+)/update/$',
        views.StudentUpdate.as_view(),
        name='student_update'),
    url(r'^(?P<school_id>\d+)/nemandi/(?P<pk>\d+)/delete/$',
        views.StudentDelete.as_view(),
        name='student_delete'),

    url(r'^(?P<school_id>\d+)/bekkur/$',
        views.StudentGroupListing.as_view(),
        name='group_listing'),
    url(r'^(?P<school_id>\d+)/bekkur/(?P<pk>\d+)/$',
        views.StudentGroupDetail.as_view(),
        name='group_detail'),
    url(r'^(?P<school_id>\d+)/bekkur/create/$',
        views.StudentGroupCreate.as_view(),
        name='group_create'),
    url(r'^(?P<school_id>\d+)/bekkur/(?P<pk>\d+)/update/$',
        views.StudentGroupUpdate.as_view(),
        name='group_update'),
    url(r'^(?P<school_id>\d+)/bekkur/(?P<pk>\d+)/delete/$',
        views.StudentGroupDelete.as_view(),
        name='group_delete'),

    url(r'^(?P<school_id>\d+)/bekkur/(?P<student_group>\d+)/próf/create/$',
        views.SurveyCreate.as_view(),
        name='survey_create'),
    url(r'^(?P<school_id>\d+)/bekkur/(?P<student_group>\d+)/próf/$',
        views.SurveyListing.as_view(),
        name='survey_listing'),
    url(r'^(?P<school_id>\d+)/bekkur/(?P<student_group>\d+)/próf/(?P<pk>\d+)/$',
        views.SurveyDetail.as_view(),
        name='survey_detail'),
    url(r'^(?P<school_id>\d+)/bekkur/(?P<student_group>\d+)/próf/(?P<pk>\d+)/update/$',
        views.SurveyUpdate.as_view(),
        name='survey_update'),
    url(r'^(?P<school_id>\d+)/bekkur/(?P<student_group>\d+)/próf/(?P<pk>\d+)/delete/$',
        views.SurveyDelete.as_view(),
        name='survey_delete'),
    url(r'^(?P<school_id>\d+)/bekkur/(?P<student_group>\d+)/próf/(?P<pk>\d+)/excel/$',
        views.survey_detail_excel,
        name='survey_detail_excel'),

    url(r'^(?P<school_id>\d+)/nemandi/(?P<student_id>\d+)/próf/(?P<survey_id>\d+)/niðurstöður/create/$',
        views.SurveyResultCreate.as_view(),
        name='survey_result_create'),
    url(r'^(?P<school_id>\d+)/nemandi/(?P<student_id>\d+)/próf/(?P<survey_id>\d+)/niðurstöður/(?P<pk>\d+)/update/$',
        views.SurveyResultUpdate.as_view(),
        name='survey_result_update'),
    url(r'^(?P<school_id>\d+)/nemandi/(?P<student_id>\d+)/próf/(?P<survey_id>\d+)/niðurstöður/(?P<pk>\d+)/delete/$',
        views.SurveyResultDelete.as_view(),
        name='survey_result_delete'),

    url(r'^(?P<school_id>\d+)/skolastjórn/$',
        views.ManagerListing.as_view(),
        name='manager_listing'),
    url(r'^skolastjórn/(?P<pk>\d+)/$',
        views.ManagerOverview.as_view(),
        name='manager_overview'),
    url(r'^(?P<school_id>\d+)/skolastjórn/(?P<pk>\d+)/$',
        views.ManagerDetail.as_view(),
        name='manager_detail'),
    url(r'^(?P<school_id>\d+)/skolastjórn/create/$',
        views.ManagerCreate.as_view(),
        name='manager_create'),
    url(r'^skolastjórn/create/import$',
        views.ManagerCreateImport.as_view(),
        name='manager_create_import'),
    url(r'^(?P<school_id>\d+)/skolastjórn/(?P<pk>\d+)/update/$',
        views.ManagerUpdate.as_view(),
        name='manager_update'),
    url(r'^(?P<school_id>\d+)/skolastjórn/(?P<pk>\d+)/delete/$',
        views.ManagerDelete.as_view(),
        name='manager_delete'),

    url(r'^(?P<school_id>\d+)/kennari/$',
        views.TeacherListing.as_view(),
        name='teacher_listing'),
    url(r'^kennari/(?P<pk>\d+)/$',
        views.TeacherOverview.as_view(),
        name='teacher_overview'),
    url(r'^(?P<school_id>\d+)/kennari/(?P<pk>\d+)/$',
        views.TeacherDetail.as_view(),
        name='teacher_detail'),
    url(r'^(?P<school_id>\d+)/kennari/create/$',
        views.TeacherCreate.as_view(),
        name='teacher_create'),
    url(r'^(?P<school_id>\d+)/kennari/create/import$',
        views.TeacherCreateImport.as_view(),
        name='teacher_create_import'),
    url(r'^(?P<school_id>\d+)/kennari/(?P<pk>\d+)/update/$',
        views.TeacherUpdate.as_view(),
        name='teacher_update'),
    url(r'^(?P<school_id>\d+)/kennari/(?P<pk>\d+)/delete/$',
        views.TeacherDelete.as_view(),
        name='teacher_delete'),

    url(r'^lykilorð/$',
        views.SurveyLoginAdminListing.as_view(),
        name='survey_login_admin_listing'),
    url(r'^lykilorð/(?P<survey_id>[\w ]+)$',
        views.SurveyLoginDetail.as_view(),
        name='survey_login_detail_all'),
    url(r'^lykilorð/(?P<survey_id>[\w ]+)/(?P<print>[\w ]+)/$',
        views.SurveyLoginDetail.as_view(),
        name='surveylogin_detail_print'),
    url(r'^(?P<school_id>\d+)/lykilorð/$',
        views.SurveyLoginListing.as_view(),
        name='survey_login_listing'),
    url(r'^(?P<school_id>\d+)/lykilorð/(?P<survey_id>[\w ]+)$',
        views.SurveyLoginDetail.as_view(),
        name='survey_login_detail'),
    url(r'^(?P<school_id>\d+)/lykilorð/(?P<survey_id>[\w ]+)/(?P<print>[\w ]+)/$',
        views.SurveyLoginDetail.as_view(),
        name='surveylogin_detail_print'),
    url(r'^próf/create$',
        views.SurveyLoginCreate.as_view(),
        name='survey_login_create'),
    url(r'^próf/(?P<survey_id>[\w ]+)/delete/$',
        views.SurveyLoginDelete.as_view(),
        name='surveylogin_delete'),

    url(r'^(?P<school_id>\d+)/hrágögn/$',
        views.ExampleSurveyListing.as_view(),
        name='example_survey_listing'),
    url(r'^(?P<school_id>\d+)/hrágögn/almennt/(?P<groupsurvey_id>\d+)/nemandi/(?P<student_id>\d+)/$',
        views.ExampleSurveyGSDetail.as_view(),
        name='example_survey_groupsurvey_detail'),
    url(r'^(?P<school_id>\d+)/hrágögn/samraemd/(?P<year>\d+)/nemandi/(?P<student_id>\d+)/(?P<quiz_type>[\w ]+)/$',
        views.ExampleSurveySamraemdDetail.as_view(),
        name='example_survey_samraemd_detail'),

    url(r'^prófadæmi/spurningar/$',
        views.ExampleSurveyQuestionAdminListing.as_view(),
        name='example_survey_question_admin_listing'),
    url(r'^prófadæmi/spurningar/create/$',
        views.ExampleSurveyQuestionAdminCreate.as_view(),
        name='example_survey_question_admin_create'),
    url(r'^prófadæmi/spurningar/(?P<pk>\d+)/update/$',
        views.ExampleSurveyQuestionAdminUpdate.as_view(),
        name='example_survey_question_admin_update'),
    url(r'^prófadæmi/spurningar/(?P<pk>\d+)/$',
        views.ExampleSurveyQuestionAdminDetail.as_view(),
        name='example_survey_question_admin_detail'),
    url(r'^prófadæmi/spurningar/(?P<pk>\d+)/delete/$',
        views.ExampleSurveyQuestionAdminDelete.as_view(),
        name='example_survey_question_admin_delete'),

    url(r'^prófadæmi/svör/$',
        views.ExampleSurveyAnswerAdminListing.as_view(),
        name='example_survey_answer_admin_listing'),
    url(r'^prófadæmi/svör/(?P<pk>\d+)/$',
        views.ExampleSurveyAnswerAdminDetail.as_view(),
        name='example_survey_answer_admin_detail'),
    url(r'prófadæmi/svör/import/$',
        views.ExampleSurveyAnswerAdminImport.as_view(),
        name='example_survey_answer_admin_import'),
    url(r'^prófadæmi/svör/(?P<pk>\d+)/delete/$',
        views.ExampleSurveyAnswerAdminDelete.as_view(),
        name='example_survey_answer_admin_delete'),

    url(r'^umsjónarmenn/$',
        views.AdminListing.as_view(),
        name='admin_listing'),
    url(r'^umsjónarmenn/create$',
        views.AdminCreate.as_view(),
        name='admin_create'),
    url(r'^umsjónarmenn/(?P<pk>\d+)/update/$',
        views.AdminUpdate.as_view(),
        name='admin_update'),
    url(r'^umsjónarmenn/próf/$',
        views.SurveyAdminListing.as_view(),
        name='survey_admin_listing'),
    url(r'^umsjónarmenn/próf/(?P<survey_title>[^\/]*)/$',
        views.StudentGroupAdminListing.as_view(),
        name='group_admin_listing'),
    url(r'^umsjónarmenn/próf/(?P<survey_title>[^\/]*)/Excel/$',
        views.group_admin_listing_excel,
        name='group_admin_listing_excel'),
    url(r'^umsjónarmenn/próf/(?P<survey_title>[^\/]*)/Excel-Mæting/$',
        views.group_admin_attendance_excel,
        name='group_admin_attendance_excel'),
]
