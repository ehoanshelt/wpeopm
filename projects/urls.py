from django.conf.urls import patterns, url

from projects import views

urlpatterns = patterns('',
	# /projects/
	url(r'^$', views.index, name='index'),
	# /projects/audit/
	url(r'^audit/$', views.audit, name='audit'),
	# /projects/5/
	url(r'^(?P<project_id>\d+)/$', views.project_detail, name='project_detail'),
	# /projects/5/edit/
	url(r'^(?P<project_id>\d+)/edit/$', views.project_edit, name='project_edit'),
	# /projects/5/complete/ -- AJAX ONLY --
	url(r'^(?P<project_id>\d+)/complete/$', views.project_complete, name='project_complete'),
	# /projects/5/start/ -- AJAX ONLY --
	url(r'^(?P<project_id>\d+)/start/$', views.project_start, name='project_start'),
	# /projects/5/archive/ -- AJAX ONLY --
	url(r'^(?P<project_id>\d+)/archive/$', views.project_archive, name='project_archive'),
	# /projects/5/delete/ -- AJAX ONLY --
	url(r'^(?P<project_id>\d+)/delete/$', views.project_delete, name='project_delete'),
	# /projects/5/clone/ 
	url(r'^(?P<project_id>\d+)/clone/$', views.project_clone, name='project_clone'),
	# /projects/add/
	url(r'^add/$', views.project_edit, name='project_add'),
	# /projects/PM/matthew/
	url(r'^PM/(?P<pm_name>\w+)/$', views.project_by_pm, name='project_by_pm'),
	# /projects/PM/matthew/tasks/
	url(r'^PM/(?P<pm_name>\w+)/tasks/$', views.tasks_by_pm, name='tasks_by_pm'),
	# /projects/5/all_tasks_to_project_pm/
	url(r'^(?P<project_id>\d+)/all_tasks_to_project_pm/$', views.all_tasks_to_project_pm, name='all_tasks_to_project_pm'),
	# /projects/tasklists/
	url(r'^tasklists/$', views.tasklist_manage, name='tasklist_manage'),
	# /projects/tasklist/5/tasks/
	url(r'^tasklist/(?P<tasklist_id>\d+)/tasks/$', views.tasklist_tasks, name='tasklist_tasks'),
	# /projects/tasklist/5/task/2/
	url(r'^tasklist/(?P<tasklist_id>\d+)/task/(?P<task_id>\d+)/$', views.task_detail, name='task_detail'),
	# /projects/tasklist/5/task_add/
	url(r'^tasklist/(?P<tasklist_id>\d+)/task_add/$', views.task_edit, name='task_add'),
	# /projects/tasklist/5/task/2/edit/
	url(r'^tasklist/(?P<tasklist_id>\d+)/task/(?P<task_id>\d+)/edit/$', views.task_edit, name='task_edit'),
	# /projects/tasklist/5/task/2/complete/ -- AJAX ONLY --
	url(r'^tasklist/(?P<tasklist_id>\d+)/task/(?P<task_id>\d+)/complete/$', views.task_complete, name='task_complete'),
	# /projects/tasklist/5/task/2/delete/ -- AJAX ONLY --
	url(r'^tasklist/(?P<tasklist_id>\d+)/task/(?P<task_id>\d+)/delete/$', views.task_delete, name='task_delete'),
	# /projects/5/tasklists/
	url(r'^(?P<project_id>\d+)/tasklists/$', views.project_tasklists, name='project_tasklists'),
	# /projects/5/tasklist/2/
	url(r'^(?P<project_id>\d+)/tasklist/<?(?P<tasklist_id>\d+)/$', views.tasklist_detail, name='tasklist_detail'),
	# /projects/5/tasklist/2/delete/
	url(r'^(?P<project_id>\d+)/tasklist/<?(?P<tasklist_id>\d+)/delete/$', views.tasklist_delete, name='tasklist_delete'),
	# /projects/5/tasklist_add/
	url(r'^(?P<project_id>\d+)/tasklist_add/$', views.tasklist_edit, name='tasklist_add'),
	# /projects/5/tasklist/add_from_template/
	url(r'^(?P<project_id>\d+)/tasklist/add_from_template/$', views.tasklist_add_from_template, name='tasklist_add_from_template'),
	# /projects/5/tasklist/2/edit/
	url(r'^(?P<project_id>\d+)/tasklist/(?P<tasklist_id>\d+)/edit/$', views.tasklist_edit, name='tasklist_edit'),
	# /projects/5/links/
	url(r'^(?P<project_id>\d+)/links/$', views.project_links, name='project_links'),
	# /project/5/link/2/
	url(r'^(?P<project_id>\d+)/link/(?P<link_id>\d+)/$', views.link_detail, name='link_detail'),
	# /projects/5/link_add/
	url(r'^(?P<project_id>\d+)/link_add/$', views.link_edit, name='link_add'),
	# /projects/5/link/2/edit/
	url(r'^(?P<project_id>\d+)/link/(?P<link_id>\d+)/edit/$', views.link_edit, name='link_edit'),
	# /projects/<object_type>/5/comment/add
	url(r'^(?P<object_type>\w+)/(?P<object_id>\d+)/comment/add/$', views.comment_edit, name='comment_add'),	
	# /projects/<object_type>/5/comment/2/edit
	url(r'^(?P<object_type>\w+)/(?P<object_id>\d+)/comment/(?P<comment_id>\d+)/edit/$', views.comment_edit, name='comment_edit'),
	# /projects/<object_type>/5/comment/2/
	url(r'^(?P<object_type>\w+)/(?P<object_id>\d+)/comment/(?P<comment_id>\d+)/$', views.comment_detail, name='comment_detail'),
	###### placeholder for risk detail
	url(r'^riskdetail/$', views.index, name='risk_detail'),
)
