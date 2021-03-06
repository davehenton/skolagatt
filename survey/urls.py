# -*- coding: utf-8 -*-
from django.conf.urls import url

from . import views

app_name = 'survey'
urlpatterns = [
    # ================ SURVEY ================ #
    url(r'^$',
        views.SurveyListing.as_view(),
        name='survey_list'),
    url(r'^(?P<pk>\d+)/$',
        views.SurveyDetail.as_view(),
        name='survey_detail'),
    url(r'^create/$',
        views.SurveyCreate.as_view(),
        name='survey_create'),
    url(r'^create_multi/$',
        views.SurveyCreateMulti.as_view(),
        name='survey_create_multi'),
    url(r'^(?P<pk>\d+)/update/$',
        views.SurveyUpdate.as_view(),
        name='survey_update'),
    url(r'^(?P<pk>\d+)/delete/$',
        views.SurveyDelete.as_view(),
        name='survey_delete'),

    # ============== SURVEY TYPE ============= #
    url(r'^type/(?P<pk>\d+)/$',
        views.SurveyTypeDetail.as_view(),
        name='survey_type_detail'),
    url(r'^type/create/$',
        views.SurveyTypeCreate.as_view(),
        name='survey_type_create'),
    url(r'^type/(?P<pk>\d+)/update/$',
        views.SurveyTypeUpdate.as_view(),
        name='survey_type_update'),
    url(r'^type/(?P<pk>\d+)/delete/$',
        views.SurveyTypeDelete.as_view(),
        name='survey_type_delete'),

    # =========== SURVEY RESOURCE ============ #
    url(r'^(?P<survey_id>\d+)/resource/(?P<pk>\d+)/$',
        views.SurveyResourceDetail.as_view(),
        name='survey_resource_detail'),
    url(r'^(?P<survey_id>\d+)/resource/create/$',
        views.SurveyResourceCreate.as_view(),
        name='survey_resource_create'),
    url(r'^(?P<survey_id>\d+)/resource/(?P<pk>\d+)/update/$',
        views.SurveyResourceUpdate.as_view(),
        name='survey_resource_update'),
    url(r'^(?P<survey_id>\d+)/resource/(?P<pk>\d+)/delete/$',
        views.SurveyResourceDelete.as_view(),
        name='survey_resource_delete'),

    # ======= SURVEY GRADING TEMPLATE ======== #
    url(r'^(?P<survey_id>\d+)/template/(?P<pk>\d+)/$',
        views.SurveyGradingTemplateDetail.as_view(),
        name='survey_template_detail'),
    url(r'^(?P<survey_id>\d+)/template/create/$',
        views.SurveyGradingTemplateCreate.as_view(),
        name='survey_template_create'),
    url(r'^(?P<survey_id>\d+)/template/(?P<pk>\d+)/update/$',
        views.SurveyGradingTemplateUpdate.as_view(),
        name='survey_template_update'),
    url(r'^(?P<survey_id>\d+)/template/(?P<pk>\d+)/delete/$',
        views.SurveyGradingTemplateDelete.as_view(),
        name='survey_template_delete'),

    # ======= SURVEY TRANSFORMATION TABLE ======== #
    url(r'^(?P<survey_id>\d+)/vorpun/(?P<pk>\d+)/$',
        views.SurveyTransformationDetail.as_view(),
        name='survey_transformation_detail'),
    url(r'^(?P<survey_id>\d+)/vorpun/create/$',
        views.SurveyTransformationCreate.as_view(),
        name='survey_transformation_create'),
    url(r'^(?P<survey_id>\d+)/vorpun/(?P<pk>\d+)/delete/$',
        views.SurveyTransformationDelete.as_view(),
        name='survey_transformation_delete'),

    # ========== SURVEY INPUT GROUP FIELD ========== #
    url(r'^(?P<survey_id>\d+)/group/(?P<pk>\d+)/$',
        views.SurveyInputGroupDetail.as_view(),
        name='survey_input_group_detail'),
    url(r'^(?P<survey_id>\d+)/group/create/$',
        views.SurveyInputGroupCreate.as_view(),
        name='survey_input_group_create'),
    url(r'^(?P<survey_id>\d+)/group/(?P<pk>\d+)/update/$',
        views.SurveyInputGroupUpdate.as_view(),
        name='survey_input_group_update'),
    url(r'^(?P<survey_id>\d+)/group/(?P<pk>\d+)/delete/$',
        views.SurveyInputGroupDelete.as_view(),
        name='survey_input_group_delete'),

    # ========== SURVEY INPUT FIELD ========== #
    url(r'^(?P<survey_id>\d+)/input/(?P<pk>\d+)/delete/$',
        views.SurveyInputFieldDelete.as_view(),
        name='survey_input_delete'),
    url(r'^(?P<survey_id>\d+)/input(?P<pk>\d+)/update/$',
        views.SurveyInputFieldUpdate.as_view(),
        name='survey_input_update'),
]
