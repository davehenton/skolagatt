from django.conf.urls import url
from .                import views


app_name = "supportandexception"
urlpatterns = [
    url(r'^skoli/(?P<school_id>\d+)/prof/(?P<groupsurvey_id>\d+)/$',
        views.ExamSupport.as_view(),
        name="examsupport"),
    url(r'^skoli/(?P<school_id>\d+)/prof/(?P<groupsurvey_id>\d+)/nemandi/(?P<pk>[0-9]+)/$',
        views.Detail.as_view(),
        name="detail"),
    url(r'^skoli/(?P<school_id>\d+)/prof/(?P<groupsurvey_id>\d+)/nemandi/(?P<pk>[0-9]+)/stuðningsúrræði/$',
        views.SupportResourceCreate.as_view(),
        name="supportresource"),
    url(r'^skoli/(?P<school_id>\d+)/prof/(?P<groupsurvey_id>\d+)/nemandi/(?P<pk>[0-9]+)/undanþágur/$',
        views.ExceptionCreate.as_view(),
        name="exception"),
    url(r'^api$',
        views.StudentWithExceptViewSet.as_view({'get': 'list'}),
        name="json"),
]
