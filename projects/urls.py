from django.conf.urls import patterns, url

from projects import views

urlpatterns = patterns('',
	# /projects/
	url(r'^$', views.index, name='index'),
	# /projects/5/
	url(r'^(?P<project_id>\d+)/$', views.project_detail, name='project_detail'),
	# /projects/5/edit/
	url(r'^(?P<project_id>\d+)/edit/$', views.project_edit, name='project_edit'),
	# /projects/add/
	url(r'^/add/$', views.project_edit, name='project_add'),
	# /projects/5/tasks/
	url(r'^(?P<project_id>\d+)/tasks/$', views.project_tasks, name='project_tasks'),
	# /project/5/task/2/
	url(r'^(?P<project_id>\d+)/task/(?P<task_id>\d+)/$', views.task_detail, name='task_detail'),
	# /projects/5/task_add/
	url(r'^(?P<project_id>\d+)/task_add/$', views.task_edit, name='task_add'),
	# /projects/5/task/2/edit/
	url(r'^(?P<project_id>\d+)/task/(?P<task_id>\d+)/edit/$', views.task_edit, name='task_edit'),
	# /projects/5/links/
	url(r'^(?P<project_id>\d+)/links/$', views.project_links, name='project_links'),
	# /project/5/link/2/
	url(r'^(?P<project_id>\d+)/link/(?P<link_id>\d+)/$', views.link_detail, name='link_detail'),
	# /projects/5/link_add/
	url(r'^(?P<project_id>\d+)/link_add/$', views.link_edit, name='link_add'),
	# /projects/5/link/2/edit/
	url(r'^(?P<project_id>\d+)/link/(?P<link_id>\d+)/edit/$', views.link_edit, name='link_edit'),
	
)
