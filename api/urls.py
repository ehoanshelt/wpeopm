from django.conf.urls import patterns, url

from piston.resource import Resource

from api.handlers import ProjectsHandler

projects_handler = Resource(ProjectsHandler)

urlpatterns = patterns('',
	url(r'^projects/$', projects_handler, name='projects_handler'),
)
