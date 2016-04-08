from django.conf.urls import url

from .views import StudentListing, StudentDetail, StudentCreate, StudentUpdate, StudentDelete
from .views import SchoolListing, SchoolDetail, SchoolCreate, SchoolUpdate, SchoolDelete


app_name = 'schools'
urlpatterns = [
    url(r'^$', StudentListing.as_view(), name='student_listing'),
    url(r'^nemendur/$', StudentListing.as_view(), name='student_listing'),
    url(r'^nemendur/(?P<pk>\d+)/$', StudentDetail.as_view(), name='student_detail'),
    url(r'^nemendur/create/$', StudentCreate.as_view(), name='student_create'),
    url(r'^nemendur/(?P<pk>\d+)/update/$', StudentUpdate.as_view(), name='student_update'),
    url(r'^nemendur/(?P<pk>\d+)/delete/$', StudentDelete.as_view(), name='student_delete'),
    url(r'^skolar/$', SchoolListing.as_view(), name='school_listing'),
    url(r'^skolar/(?P<pk>\d+)/$', SchoolDetail.as_view(), name='school_detail'),
    url(r'^skolar/create/$', SchoolCreate.as_view(), name='school_create'),
    url(r'^skolar/(?P<pk>\d+)/update/$', SchoolUpdate.as_view(), name='school_update'),
    url(r'^skolar/(?P<pk>\d+)/delete/$', SchoolDelete.as_view(), name='school_delete'),

]