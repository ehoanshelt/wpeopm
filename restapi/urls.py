from django.conf.urls import patterns, url

urlpatterns = patterns('restapi.views',
	url(r'^links/$', 'link_list'),
	url(r'^links/(?P<pk>[0-9]+)/$', 'link_detail'),
)