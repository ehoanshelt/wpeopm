from django.conf.urls import patterns, url

from rest_framework.urlpatterns import format_suffix_patterns

from restapi import views

urlpatterns = patterns('',
	url(r'^links/$', views.LinkList.as_view()),
	url(r'^links/(?P<pk>[0-9]+)/$', views.LinkDetail.as_view()),
)

urlpatterns = format_suffix_patterns(urlpatterns)
