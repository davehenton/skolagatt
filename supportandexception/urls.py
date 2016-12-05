from django.conf.urls import url
from django.conf      import settings
from .                import views


app_name = 'supportandexception'
urlpatterns = [
    url(r'^' + settings.SUBDIRECTORY + '(?P<school_id>\d+)/$',
        views.ExamSupport.as_view(),
        name='examsupport'),
    url(r'^' + settings.SUBDIRECTORY + '(?P<school_id>\d+)/nemandi/(?P<pk>[0-9]+)/$',
        views.Detail.as_view(),
        name='detail'),
    url(r'^' + settings.SUBDIRECTORY + '(?P<school_id>\d+)/nemandi/(?P<pk>[0-9]+)/stuðningsúrræði/$',
        views.SupportreResourceCreate.as_view(),
        name='supportresource'),
    url(r'^' + settings.SUBDIRECTORY + '(?P<school_id>\d+)/nemandi/(?P<pk>[0-9]+)/undanþágur/$',
        views.ExceptionCreate.as_view(),
        name='exception'),
    url(r'^' + settings.SUBDIRECTORY + 'api$',
        views.StudentWithExceptViewSet.as_view({'get': 'list'}),
        name='json'),
]
