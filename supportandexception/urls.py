from django.conf.urls import url
from django.conf      import settings
from .views           import *


app_name = 'supportandexception'
urlpatterns = [
	url(r'^'+settings.SUBDIRECTORY+'(?P<school_id>\d+)/$',
		ExamSupport.as_view(),
		name='examsupport'),
	url(r'^'+settings.SUBDIRECTORY+'(?P<school_id>\d+)/nemandi/(?P<pk>[0-9]+)/$',
		Detail.as_view(),
		name='detail'),
	url(r'^'+settings.SUBDIRECTORY+'(?P<school_id>\d+)/nemandi/(?P<pk>[0-9]+)/stuðningsúrræði/$',
		SupportreResourceCreate.as_view(),
		name='supportresource'),
	url(r'^'+settings.SUBDIRECTORY+'(?P<school_id>\d+)/nemandi/(?P<pk>[0-9]+)/undanþágur/$',
		ExceptionCreate.as_view(),
		name='exception'),
	url(r'^'+settings.SUBDIRECTORY+'api$',
		StudentWithExceptViewSet.as_view({'get': 'list'}),
		name='json'),
]