from django.conf.urls import url

from .views import StudentListing, StudentDetail, StudentCreate, StudentUpdate, StudentDelete


app_name = 'students'
urlpatterns = [
    url(r'^$', StudentListing.as_view(), name='listing'),
    url(r'^(?P<pk>\d+)/$', StudentDetail.as_view(), name='detail'),
    url(r'^create/$', StudentCreate.as_view(), name='create'),
    url(r'^(?P<pk>\d+)/update/$', StudentUpdate.as_view(), name='update'),
    url(r'^(?P<pk>\d+)/delete/$', StudentDelete.as_view(), name='delete'),
]