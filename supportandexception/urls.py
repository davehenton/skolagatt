

from django.conf.urls import url

from . import views


app_name = 'supportandexception'
urlpatterns = [
	url(r'^(?P<school_id>\d+)/undanþágur/$',views.ExamSupport.as_view(),name='examsupport'),
	url(r'^(?P<school_id>\d+)/undanþágur/(?P<student_id>[0-9]+)/$',views.Detail.as_view(),name='detail'),
	url(r'^(?P<school_id>\d+)/undanþágur/(?P<student_id>[0-9]+)/create/$',views.create_post, name='create_post'),
	url(r'^(?P<school_id>\d+)/undanþágur/(?P<student_id>[0-9]+)/supportresource/create/$',views.SupportreResourceCreate.as_view(),name='supportresource'),
	url(r'^(?P<school_id>\d+)/undanþágur/(?P<student_id>[0-9]+)/exception/$',views.ExceptionCreate.as_view(),name='exception'),
	url(r'^(?P<school_id>\d+)/undanþágur/(?P<student_id>[0-9]+)/exception/exception_senda/$',views.exception_post,name='exception_post'),
	url(r'^(?P<school_id>\d+)/undanþágur/(?P<student_id>[0-9]+)/exception/exception_eyða/$',views.exception_cancel,name='exception_cancel'),
]