from django.conf.urls import url

from .views import StudentListing, StudentDetail, StudentCreate, StudentCreateImport, StudentUpdate, StudentDelete
from .views import SchoolListing, SchoolDetail, SchoolCreate, SchoolUpdate, SchoolDelete
from .views import StudentGroupListing, StudentGroupDetail, StudentGroupCreate, StudentGroupUpdate, StudentGroupDelete
from .views import ManagerListing, ManagerDetail, ManagerCreate, ManagerUpdate, ManagerDelete
from .views import TeacherListing, TeacherDetail, TeacherCreate, TeacherUpdate, TeacherDelete
from .views import SurveyListing, SurveyDetail, SurveyCreate, SurveyUpdate, SurveyDelete

app_name = 'schools'
urlpatterns = [
    url(r'^$', SchoolListing.as_view(), name='school_listing'),
    url(r'^(?P<pk>\d+)/$', SchoolDetail.as_view(), name='school_detail'),
    url(r'^create/$', SchoolCreate.as_view(), name='school_create'),
    url(r'^(?P<pk>\d+)/update/$', SchoolUpdate.as_view(), name='school_update'),
    url(r'^(?P<pk>\d+)/delete/$', SchoolDelete.as_view(), name='school_delete'),

    url(r'^(?P<school_id>\d+)/nemandi/$', StudentListing.as_view(), name='student_listing'),
    url(r'^(?P<school_id>\d+)/nemandi/(?P<pk>\d+)/$', StudentDetail.as_view(), name='student_detail'),
    url(r'^(?P<school_id>\d+)/nemandi/create/$', StudentCreate.as_view(), name='student_create'),
    url(r'^(?P<school_id>\d+)/nemandi/create/import$', StudentCreateImport.as_view(), name='student_create_import'),
    url(r'^(?P<school_id>\d+)/nemandi/(?P<pk>\d+)/update/$', StudentUpdate.as_view(), name='student_update'),
    url(r'^(?P<school_id>\d+)/nemandi/(?P<pk>\d+)/delete/$', StudentDelete.as_view(), name='student_delete'),

    url(r'^(?P<school_id>\d+)/bekkur/$', StudentGroupListing.as_view(), name='group_listing'),
    url(r'^(?P<school_id>\d+)/bekkur/(?P<pk>\d+)/$', StudentGroupDetail.as_view(), name='group_detail'),
    url(r'^(?P<school_id>\d+)/bekkur/create/$', StudentGroupCreate.as_view(), name='group_create'),
    url(r'^(?P<school_id>\d+)/bekkur/(?P<pk>\d+)/update/$', StudentGroupUpdate.as_view(), name='group_update'),
    url(r'^(?P<school_id>\d+)/bekkur/(?P<pk>\d+)/delete/$', StudentGroupDelete.as_view(), name='group_delete'),

    url(r'^(?P<school_id>\d+)/skolastjorn/$', ManagerListing.as_view(), name='manager_listing'),
    url(r'^(?P<school_id>\d+)/skolastjorn/(?P<pk>\d+)/$', ManagerDetail.as_view(), name='manager_detail'),
    url(r'^(?P<school_id>\d+)/skolastjorn/create/$', ManagerCreate.as_view(), name='manager_create'),
    url(r'^(?P<school_id>\d+)/skolastjorn/(?P<pk>\d+)/update/$', ManagerUpdate.as_view(), name='manager_update'),
    url(r'^(?P<school_id>\d+)/skolastjorn/(?P<pk>\d+)/delete/$', ManagerDelete.as_view(), name='manager_delete'),

    url(r'^(?P<school_id>\d+)/kennari/$', TeacherListing.as_view(), name='teacher_listing'),
    url(r'^(?P<school_id>\d+)/kennari/(?P<pk>\d+)/$', TeacherDetail.as_view(), name='teacher_detail'),
    url(r'^(?P<school_id>\d+)/kennari/create/$', TeacherCreate.as_view(), name='teacher_create'),
    url(r'^(?P<school_id>\d+)/kennari/(?P<pk>\d+)/update/$', TeacherUpdate.as_view(), name='teacher_update'),
    url(r'^(?P<school_id>\d+)/kennari/(?P<pk>\d+)/delete/$', TeacherDelete.as_view(), name='teacher_delete'),

    url(r'^(?P<school_id>\d+)/könnun/$', SurveyListing.as_view(), name='survey_listing'),
    url(r'^(?P<school_id>\d+)/könnun/(?P<pk>\d+)/$', SurveyDetail.as_view(), name='survey_detail'),
    url(r'^(?P<school_id>\d+)/könnun/create/$', SurveyCreate.as_view(), name='survey_create'),
    url(r'^(?P<school_id>\d+)/könnun/(?P<pk>\d+)/update/$', SurveyUpdate.as_view(), name='survey_update'),
    url(r'^(?P<school_id>\d+)/könnun/(?P<pk>\d+)/delete/$', SurveyDelete.as_view(), name='survey_delete'),


]