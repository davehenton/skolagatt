

from django.conf.urls import url
from django.conf import settings
from .views import *


app_name = 'supportandexception'
urlpatterns = [
	url(r'^'+settings.SUBDIRECTORY+'(?P<school_id>\d+)/$',ExamSupport.as_view(),name='examsupport'),
	url(r'^'+settings.SUBDIRECTORY+'(?P<school_id>\d+)/(?P<pk>[0-9]+)/$',Detail.as_view(),name='detail'),
	url(r'^'+settings.SUBDIRECTORY+'(?P<school_id>\d+)/(?P<pk>[0-9]+)/ný_stuðningsúrræði/$',SupportreResourceCreate.as_view(),name='supportresource'),
	url(r'^'+settings.SUBDIRECTORY+'(?P<school_id>\d+)/(?P<pk>[0-9]+)/nýjar_undanþágur/$',ExceptionCreate.as_view(),name='exception'),
	url(r'^'+settings.SUBDIRECTORY+'api$', StudentWithExceptViewSet.as_view({'get': 'list'}), name='json'),
]