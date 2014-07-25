import datetime
import json

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.views import login
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.http import HttpResponse, HttpResponseForbidden, HttpResponseNotFound
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from projects.decorators import secure_required
from projects.forms import ProjectForm, TaskListForm, TaskForm, LinkForm, CommentForm
from projects.models import Category, STATUS_CHOICES, Project, TaskList, Task, Dependency, Risk, Link, Comment
from projects.utils import notify_webhook

@secure_required
def ssl_login(request, *args, **kwargs):
	# Creating this view to force /login/ page to https.
	if request.method == 'POST':
		if not request.POST.get('remember', None):
			request.session.set_expiry(0)

	return login(request, *args, **kwargs)

def index(request):
	if not request.user.is_authenticated():
		return render(request, 'projects/home.html', {})
	active_project_list = Project.objects.filter(isDeleted=False).filter(~Q(status='C')).order_by('acctName')
	archived_project_list = Project.objects.filter(isArchived=True, isDeleted=False).order_by('acctName')
	PM_list = Project.objects.order_by('PM__username').values('PM__username').distinct()
	AM_list = Project.objects.values_list('AM', flat=True).distinct()
	AM_list = filter(None, AM_list)
	context = {
		'active_project_list': active_project_list,
		'archived_project_list': archived_project_list,
		'PM_list': PM_list,
		'AM_list': AM_list,
	}
	return render(request, 'projects/index.html', context)

# keeping this outside of login for this point until we do google apps SSO
def audit(request):
	"""
	Audits the projects in the system. Looks for danger signs or other incompletions:
	* Project has a start date in the past but is not marked as In Progress
	* Project has a due date in the past but is not marked Complete
	"""
	active_projects = Project.objects.filter(isDeleted=False).filter(~Q(status='C')).order_by('acctName')
	today = datetime.datetime.now()
	return render(request, 'projects/audit.html', {'active_projects': active_projects, 'today': today})

@login_required
def project_by_pm(request, pm_name):
	project_list = Project.objects.filter(PM__username=pm_name).order_by('acctName')
	return render(request, 'projects/projects_by_pm.html', {'PM': pm_name, 'project_list': project_list})

@login_required
def tasks_by_pm(request, pm_name):
	task_list = Task.objects.filter(PM__username=pm_name).order_by('dueDate')
	return render(request, 'projects/tasks_by_pm.html', {'PM': pm_name, 'task_list': task_list})

@login_required
def project_detail(request, project_id):
	project = get_object_or_404(Project, pk=project_id)
	return render(request, 'projects/project_detail.html', {'project': project})

@login_required
def project_edit(request, project_id=None):
	if project_id:
		project = get_object_or_404(Project, pk=project_id)
	else:
		project = Project()
		project.acctName = 'New Project'
		project.created = timezone.now()
	if request.POST:
		form = ProjectForm(request.POST, instance=project)
		if form.is_valid():
			form.save()
			notify_webhook('project', project.id)
			return redirect('index')
	else:
		form = ProjectForm(instance=project)
	
	return render(request, 'projects/project_edit.html', {'form': form, 'project': project})

@login_required
def project_clone(request, project_id):
	"""
	Clones a project to a new project, setting the PM to request.user and unassigning all tasks and removing all dates.
	"""
	project = get_object_or_404(Project, pk=project_id)
	new_project = Project()
	new_project.acctName = 'Cloned Project'
	new_project.created = timezone.now()
	new_project.category = project.category
	new_project.PM = request.user
	new_project.AM = project.AM
	new_project.startDate = timezone.now().date()
	new_project.isCompleted = False
	new_project.isArchived = False
	new_project.isDeleted = False
	new_project.save()
	notify_webhook('project', new_project.id)
	tasklists = TaskList.objects.filter(project=project)
	for tasklist in tasklists:
		new_tasklist = TaskList()
		new_tasklist.created = timezone.now()
		new_tasklist.name = tasklist.name
		new_tasklist.description = tasklist.description
		new_tasklist.isTemplate = False
		new_tasklist.project = new_project
		new_tasklist.isDeleted = False
		new_tasklist.save()
		tasks = Task.objects.filter(tasklist=tasklist)
		taskMap = {} # hold map of old to new task IDs to recreate dependencies on clone
		for task in tasks:
			new_task = Task()
			new_task.created = timezone.now()
			new_task.tasklist = new_tasklist
			new_task.name = task.name
			new_task.PM = None
			new_task.description = task.description
			new_task.status = 'N'
			new_task.save()
			taskMap[task.id] = new_task.id
	for key in taskMap:
		dep = Dependency.objects.filter(task=key)
		for d in dep:
			new_dep = Dependency()
			new_dep.task = Task.objects.get(pk=taskMap[key])
			new_dep.dependsOn = Task.objects.get(pk=taskMap[d.dependsOn.id])
			new_dep.save()

	return redirect(reverse('project_edit', kwargs={'project_id': new_project.id}))

@login_required
def project_complete(request, project_id):
	if not request.is_ajax():
		return HttpResponseForbidden()
	project = get_object_or_404(Project, pk=project_id)
	project.status = 'C'
	project.completedDate = timezone.now()
	if project.endDate is None:
		project.endDate = project.completedDate
	project.save()
	notify_webhook('project', project.id)
	json_data = json.dumps({"HTTPRESPONSE":1})
	return HttpResponse(json_data, mimetype="application/json")

@login_required
def project_archive(request, project_id):
	if not request.is_ajax():
		return HttpResponseForbidden()
	project = get_object_or_404(Project, pk=project_id)
	project.isArchived = True
	project.save()
	notify_webhook('project', project.id)
	json_data = json.dumps({"HTTPRESPONSE":1})
	return HttpResponse(json_data, mimetype="application/json")

@login_required
def project_delete(request, project_id):
	if not request.is_ajax():
		return HttpResponseForbidden()
	project = get_object_or_404(Project, pk=project_id)
	project.isDeleted = True
	project.save()
	notify_webhook('project', project.id)
	json_data = json.dumps({"HTTPRESPONSE":1})
	return HttpResponse(json_data, mimetype="application/json")

@login_required
def tasklist_tasks(request, tasklist_id):
	tasklist = get_object_or_404(TaskList, pk=tasklist_id)
	return render(request, 'projects/tasklist_tasks.html', {'tasklist': tasklist})

@login_required
def task_detail(request, tasklist_id, task_id):
	tasklist = get_object_or_404(TaskList, pk=tasklist_id)
	task = get_object_or_404(Task, pk=task_id)
	return render(request, 'projects/task_detail.html', {'task': task})

@login_required
def task_edit(request, tasklist_id, task_id=None):
	tasklist = get_object_or_404(TaskList, pk=tasklist_id)
	other_tasks = Task.objects.filter(tasklist=tasklist)
	if task_id:
		task = get_object_or_404(Task, pk=task_id)
		other_tasks = other_tasks.filter(~Q(id=task_id))
	else:
		task = Task()
		task.created = timezone.now()
		task.tasklist = tasklist
	rt_ids = [rt.dependsOn.id for rt in task.task_set.all()]
	if request.POST:
		form = TaskForm(request.POST, instance=task)
		if form.is_valid():
			form.save()
			otList = request.POST.getlist("other-tasks")
			for ot in otList:
				# add checked tasks
				try:
					dep = Dependency.objects.get(task__id=task.id, dependsOn__id=ot)
				except:
					dep = None
				if not dep:
					# we have to add the dependency because it's not there
					dep = Dependency()
					dep.task = task
					do = get_object_or_404(Task, pk=ot)
					dep.dependsOn = do
					dep.save()
			removed_tasks = list(set(rt_ids) - set(otList))	
			# remove any tasks that were unchecked
			for removed in removed_tasks:

				try:
					r = Dependency.objects.get(task__id=task.id, dependsOn__id=removed)
				except:
					r = None # invalid data, ignore
				if r:
					r.delete()
		
			notify_webhook('task', task.id)
			return redirect('tasklist_detail', project_id=task.tasklist.project.id, tasklist_id=task.tasklist.id)
	else:
		form = TaskForm(instance=task)
	
	return render(request, 'projects/task_edit.html', {'form': form, 'task': task, 'other_tasks': other_tasks, 'rt_ids': rt_ids})

@login_required
def task_complete(request, tasklist_id, task_id):
	if not request.is_ajax():
		return HttpResponseForbidden()
	task = get_object_or_404(Task, pk=task_id)
	if not task.can_be_completed:
		json_data = json.dumps({"HTTPRESPONSE":2})
		return HttpResponse(json_data, mimetype="application/json")
	task.status = 'C'
	task.completedDate = timezone.now()
	if task.endDate is None:
		task.endDate = task.completedDate
	task.save()
	notify_webhook('task', task.id)
	json_data = json.dumps({"HTTPRESPONSE":1})
	return HttpResponse(json_data, mimetype="application/json")

@login_required
def all_tasks_to_project_pm(request, project_id):
	if not request.is_ajax():
		return HttpResponseForbidden
	project = get_object_or_404(Project, pk=project_id)
	tasklists = TaskList.objects.filter(project__id=project_id, isDeleted=False)
	for tasklist in tasklists:
		tasks = Task.objects.filter(tasklist=tasklist)
		for task in tasks:
			task.PM = project.PM
			task.save()
			notify_webhook('task', task.id)
	json_data = json.dumps({"HTTPRESPONSE":1})
	return HttpResponse(json_data, mimetype="application/json")

@login_required
def project_tasklists(request, project_id):
	project = get_object_or_404(Project, pk=project_id)
	return render(request, 'projects/project_tasklists.html', {'project': project})

@login_required
def tasklist_add_from_template(request, project_id):
	project = get_object_or_404(Project, pk=project_id)
	if request.POST:
		templates = request.POST.getlist("templates")
		if templates:
			for tl_id in templates:
				template = get_object_or_404(TaskList, pk=tl_id)
				tasklist = TaskList()
				tasklist.created = timezone.now()
				tasklist.name = template.name
				tasklist.description = template.description
				tasklist.isTemplate = False
				tasklist.project = project
				tasklist.isDeleted = False
				tasklist.save()
				notify_webhook('tasklist', tasklist.id)
				tasks = Task.objects.filter(tasklist=template)
				for each_task in tasks:
					task = Task()
					task.created = timezone.now()
					task.tasklist = tasklist
					task.name = each_task.name
					task.PM = each_task.PM
					task.description = each_task.description
					task.isCompleted = False
					task.save()
		return redirect('project_tasklists', project_id=project.id)
	tasklist_template_list = TaskList.objects.filter(isTemplate=True, isDeleted=False)
	return render(request, 'projects/tasklist_add_from_template.html', {'project': project, 'tasklist_template_list': tasklist_template_list})

@login_required
def tasklist_manage(request):
	"""
	This may be a misnomer -- this is to configure globally-accessible tasklist templates.
	"""
	tasklist_template_list = TaskList.objects.filter(isTemplate=True, isDeleted=False)
	return render(request, 'projects/tasklist_manage.html', {'tasklist_template_list': tasklist_template_list})

@login_required
def tasklist_detail(request, project_id, tasklist_id):
	if (project_id != '0'):
		project = get_object_or_404(Project, pk=project_id)
	tasklist = get_object_or_404(TaskList, pk=tasklist_id)
	today = timezone.now()
	return render(request, 'projects/tasklist_detail.html', {'tasklist': tasklist, 'today': today})

@login_required
def tasklist_delete(request, project_id, tasklist_id):
	if not request.is_ajax():
		return HttpResponseForbidden
	if (project_id != '0'):
		project = get_object_or_404(Project, pk=project_id)
	tasklist = get_object_or_404(TaskList, pk=tasklist_id)
	tasklist.isDeleted = True
	tasklist.save()
	notify_webhook('tasklist', tasklist.id)
	json_data = json.dumps({"HTTPRESPONSE":1})
	return HttpResponse(json_data, mimetype="application/json")

@login_required
def tasklist_edit(request, project_id, tasklist_id=None):
	if (project_id != '0'):
		project = get_object_or_404(Project, pk=project_id)
	else:
		project = None
	if tasklist_id:
		tasklist = get_object_or_404(TaskList, pk=tasklist_id)
	else:
		tasklist = TaskList()
		tasklist.created = timezone.now()
		tasklist.isDeleted = False
		if project is not None:
			tasklist.project = project
			tasklist.isTemplate = False
		else:
			tasklist.isTemplate = True
	if request.POST:
		form = TaskListForm(request.POST, instance=tasklist)
		if form.is_valid():
			form.save()
			notify_webhook('tasklist', tasklist.id)
			if project:
				return redirect('project_detail', project_id=tasklist.project.id)
			else:
				return redirect('tasklist_manage')
	else:
		form = TaskListForm(instance=tasklist)
	
	return render(request, 'projects/tasklist_edit.html', {'form': form, 'project': project, 'tasklist': tasklist})

@login_required
def project_links(request, project_id):
	project = get_object_or_404(Project, pk=project_id)
	return render(request, 'projects/project_links.html', {'project': project})

@login_required
def link_detail(request, project_id, link_id):
	project = get_object_or_404(Project, pk=project_id)
	link = get_object_or_404(Link, pk=link_id)
	return render(request, 'projects/link_detail.html', {'link': link})

@login_required
def link_edit(request, project_id, link_id=None):
	project = get_object_or_404(Project, pk=project_id)
	if link_id:
		link = get_object_or_404(Link, pk=link_id)
	else:
		link = Link()
		link.created = timezone.now()
		link.project = project
	if request.POST:
		form = LinkForm(request.POST, instance=link)
		if form.is_valid():
			form.save()
			notify_webhook('link', link.id)
			return redirect('project_detail', project_id=link.project.id)
	else:
		form = LinkForm(instance=link)
	
	return render(request, 'projects/link_edit.html', {'form': form, 'link': link})

def f(x):
	"""
	This is to emulate a switch statement for comment_[action](). This is outside the comment_action() function to avoid the dictionary 
	having to be re-built whenever the comment_action() functions are called.
	"""
	return {
		'project': 'P',
		'task': 'T',
		'risk': 'R',
		'link': 'L',
	}.get(x, '0') # return 0 if it's not a valid entry

@login_required
def comment_edit(request, object_type, object_id, comment_id=None):
	"""
	Extensible and generic template based on the object_type.
	"""
	parent_type = f(object_type)
	if parent_type == '0':
		return HttpResponseNotFound
	project = None
	task = None
	risk = None
	link = None
	if parent_type == 'P':
		project = get_object_or_404(Project, pk=object_id)
		return_url = reverse('project_detail', kwargs={'project_id': object_id})
	if parent_type == 'T':
		task = get_object_or_404(Task, pk=object_id)
		return_url = reverse('task_detail', kwargs={'task_id': object_id})
	if parent_type == 'R':
		risk = get_object_or_404(Risk, pk=object_id)
		return_url = reverse('risk_detail', kwargs={'risk_id': object_id})
	if parent_type == 'L':
		link = get_object_or_404(Link, pk=object_id)
		return_url = reverse('link_detail', kwargs={'project_id': link.project.id, 'link_id': object_id})
	if comment_id:
		comment = get_object_or_404(Comment, pk=comment_id)
		if parent_type == 'P':
			comment.project = project
		if parent_type == 'T':
			comment.task = task
		if parent_type == 'R':
			comment.risk = risk
		if parent_type == 'L':
			comment.link = link
	else:
		comment = Comment()
		comment.created = timezone.now()
	if request.POST:
		form = CommentForm(request.POST, instance=comment, parent_object=parent_type)
		if form.is_valid():
			form.save()
			return redirect(return_url)
	else:
		form = CommentForm(instance=comment, parent_object=parent_type)
	return render(request, 'projects/comment_edit.html', {'form': form})

@login_required
def comment_detail(request, object_type, object_id, comment_id):
	parent_type = f(object_type)
	if parent_type == '0':
		return HttpResponseNotFound
	project = None
	task = None
	risk = None
	link = None
	if parent_type == 'P':
		project = get_object_or_404(Project, pk=object_id)
		return_url = reverse('project_detail', kwargs={'project_id': object_id})
	if parent_type == 'T':
		task = get_object_or_404(Task, pk=object_id)
		return_url = reverse('task_detail', kwargs={'tasklist_id': task.tasklist.id, 'task_id': object_id})
	if parent_type == 'R':
		risk = get_object_or_404(Risk, pk=object_id)
		return_url = reverse('risk_detail', kwargs={'risk_id': object_id})
	if parent_type == 'L':
		link = get_object_or_404(Link, pk=object_id)
		return_url = reverse('link_detail', kwargs={'project_id': link.project.id, 'link_id': object_id})
	if comment_id:
		comment = get_object_or_404(Comment, pk=comment_id)
	return render(request, 'projects/comment_detail.html', {'comment': comment, 'project': project, 'task': task, 'risk': risk, 'link': link})