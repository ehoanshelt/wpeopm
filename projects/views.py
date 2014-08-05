import calendar
import datetime
import json
import markdown

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.views import login
from django.core.urlresolvers import reverse
from django.db.models import Count, Q
from django.http import HttpResponse, HttpResponseForbidden, HttpResponseNotFound
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from projects.decorators import secure_required
from projects.forms import ProjectForm, TaskListForm, TaskForm, LinkForm, CommentForm
from projects.models import Category, HANDOFF_CHOICE_DICT, STATUS_CHOICES, Project, TaskList, Task, Dependency, Risk, Link, Comment
from projects.utils import JsonHttpResponse, notify_webhook

@secure_required
def ssl_login(request, *args, **kwargs):
	# Creating this view to force /login/ page to https.
	if request.method == 'POST':
		if not request.POST.get('remember', None):
			request.session.set_expiry(0)

	return login(request, *args, **kwargs)

def index(request):
	if not request.user.is_authenticated():

		autherror = request.GET.get('autherror', None)
		if autherror is not None:
			messages.add_message(request, messages.ERROR, 'Error logging in. Please try again.')
		return render(request, 'projects/home.html', {})
	active_project_list = Project.objects.filter(isDeleted=False).filter(~Q(status='C')).extra(select={'lower_name':'lower(acctName)'}).order_by('lower_name')
	archived_project_list = Project.objects.filter(isArchived=True, isDeleted=False).extra(select={'lower_name':'lower(acctName)'}).order_by('lower_name')
	PM_list = Project.objects.order_by('PM__username').values('PM__username').distinct()
	AM_list = Project.objects.order_by('AM').values_list('AM', flat=True).distinct()
	AM_list = filter(None, AM_list)
	today = datetime.date.today()
	startOfWeek = today - datetime.timedelta(days=today.weekday())
	endOfWeek = startOfWeek + datetime.timedelta(days=7)
	projects_completed_this_week = Project.objects.filter(status='C', completedDate__gte=startOfWeek, completedDate__lte=endOfWeek).order_by('completedDate')
	context = {
		'active_project_list': active_project_list,
		'archived_project_list': archived_project_list,
		'PM_list': PM_list,
		'AM_list': AM_list,
		'projects_completed_this_week': projects_completed_this_week,
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

def dashboard(request):
	"""
	Dashboard view for charts.
	"""
	# start off with a bunch of date calculations to build the graphs with
	now = datetime.datetime.now()
	thisMonth = now.month
	thisYear = now.year
	firstOfThisMonth = datetime.date(thisYear, thisMonth, 1)
	lastDayThisMonth = calendar.monthrange(thisYear, thisMonth)[1]
	lastOfThisMonth = datetime.date(thisYear, thisMonth, lastDayThisMonth)
	if thisMonth < 4:
		firstMonthThisQuarter = 1
		lastMonthThisQuarter = 3
	elif thisMonth < 7:
		firstMonthThisQuarter = 4
		lastMonthThisQuarter = 6
	elif thisMonth < 10:
		firstMonthThisQuarter = 7
		lastMonthThisQuarter = 9
	else:
		firstMonthThisQuarter = 10
		lastMonthThisQuarter = 12
	firstOfThisQuarter = datetime.date(thisYear, firstMonthThisQuarter, 1)
	lastDayThisQuarter = calendar.monthrange(thisYear, lastMonthThisQuarter)[1]
	lastOfThisQuarter = datetime.date(thisYear, lastMonthThisQuarter, lastDayThisQuarter)

	# Chart 1 -- Active projects by category
	projects_category_active = Project.objects.values('category__name').filter(isDeleted=False).filter(~Q(status='C')).order_by().annotate(Count('category'))
	projects_category_month = Project.objects.values('category__name').filter(isDeleted=False, created__gte=firstOfThisMonth, created__lte=lastOfThisMonth).order_by().annotate(Count('category'))
	projects_category_quarter = Project.objects.values('category__name').filter(isDeleted=False, created__gte=firstOfThisQuarter, created__lte=lastOfThisQuarter).order_by().annotate(Count('category'))

	# Chart 2 -- Handoff type vs. customer engagement
	handoff_engagement = []
	for hc in HANDOFF_CHOICE_DICT:
		engaged = Project.objects.filter(handoffType=hc, customerEngaged=True).count()
		unengaged = Project.objects.filter(handoffType=hc, customerEngaged=False).count()
		handoff_engagement.append((HANDOFF_CHOICE_DICT[hc], engaged, unengaged))

	# Chart 3 -- Projects summary
	inProgress = Project.objects.filter(isDeleted=False, status='I').count()
	completed = Project.objects.filter(isDeleted=False, status='C').count()
	projects_summary = {'inProgress': inProgress, 'completed': completed}

	return render(request, 'projects/dashboard.html', 
		{
			'projects_category_active': projects_category_active,
			'projects_category_month': projects_category_month,
			'projects_category_quarter': projects_category_quarter,
			'handoff_engagement': handoff_engagement,
			'projects_summary': projects_summary,
		}
	)

@login_required
def project_by_pm(request, pm_name):
	project_list = Project.objects.filter(PM__username=pm_name).order_by('acctName')
	return render(request, 'projects/projects_by_pm.html', {'PM': pm_name, 'project_list': project_list})

@login_required
def project_by_am(request, am_name):
	project_list = Project.objects.filter(AM=am_name).order_by('acctName')
	return render(request, 'projects/projects_by_am.html', {'AM': am_name, 'project_list': project_list})

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
		add_or_edit = 'Edit'
	else:
		project = Project()
		add_or_edit = 'Add'
	form = ProjectForm(request.POST or None, instance=project)
	if form.is_valid():
		project = form.save()
		project.save()
		notify_webhook('project', project.id)
		return redirect('project_detail', project.id)

	return render(request, 'projects/project_edit.html', {'form': form, 'project': project, 'add_or_edit': add_or_edit})

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
def project_start(request, project_id):
	if not request.is_ajax():
		return HttpResponseForbidden()
	project = get_object_or_404(Project, pk=project_id)
	project.status = 'I'
	if project.startDate is None:
		project.startDate = timezone.now()
	project.save()
	notify_webhook('project', project.id)
	return JsonHttpResponse({"HTTPRESPONSE":1})

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
	return JsonHttpResponse({"HTTPRESPONSE":1})

@login_required
def project_archive(request, project_id):
	if not request.is_ajax():
		return HttpResponseForbidden()
	project = get_object_or_404(Project, pk=project_id)
	project.isArchived = True
	project.save()
	notify_webhook('project', project.id)
	return JsonHttpResponse({"HTTPRESPONSE":1})

@login_required
def project_delete(request, project_id):
	if not request.is_ajax():
		return HttpResponseForbidden()
	project = get_object_or_404(Project, pk=project_id)
	project.isDeleted = True
	project.save()
	notify_webhook('project', project.id)
	return JsonHttpResponse({"HTTPRESPONSE":1})

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
		add_or_edit = 'Edit'
		other_tasks = other_tasks.filter(~Q(id=task_id))
	else:
		task = Task()
		add_or_edit = 'Add'
		task.created = timezone.now()
		task.tasklist = tasklist
	rt_ids = [rt.dependsOn.id for rt in task.task_set.all()]
	form = TaskForm(request.POST or None, instance=task)
	if form.is_valid():
		form.save()
		otList = request.POST.getlist("other-tasks")
		for ot in otList:
			# add checked tasks
			dep = Dependency.objects.get_or_none(task__id=task.id, dependsOn__id=ot)
			if not dep:
				dep = Dependency()
				dep.task = task
				do = get_object_or_404(Task, pk=ot)
				dep.dependsOn = do
				dep.save()
		removed_tasks = list(set(rt_ids) - set(otList))
		# remove any tasks that were unchecked
		for removed in removed_tasks:
			r = Dependency.objects.get_or_none(task__id=task.id, dependsOn__id=ot)
			if r:
				r.delete()
		notify_webhook('task', task.id)
		if tasklist.project:
			project_id = tasklist.project.id
		else:
			project_id = 0
		return redirect('tasklist_detail', project_id=project_id, tasklist_id=task.tasklist.id)

	return render(request, 'projects/task_edit.html', {'form': form, 'task': task, 'other_tasks': other_tasks, 'rt_ids': rt_ids, 'add_or_edit': add_or_edit})

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
def task_delete(request, tasklist_id, task_id):
	if not request.is_ajax():
		return HttpResponseForbidden()
	task = get_object_or_404(Task, pk=task_id)
	if task.has_dependencies:
		return JsonHttpResponse({"HTTPRESPONSE":2})
	task.delete()
	return JsonHttpResponse({"HTTPRESPONSE":1})

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
		return redirect('project_detail', project_id=project.id)
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
	project = Project.objects.get_or_none(pk=project_id)
	if tasklist_id:
		tasklist = get_object_or_404(TaskList, pk=tasklist_id)
		add_or_edit = 'Edit'
	else:
		tasklist = TaskList()
		add_or_edit = 'Add'
		if project is not None:
			tasklist.project = project
			tasklist.isTemplate = False
		else:
			tasklist.isTemplate = True
	form = TaskListForm(request.POST or None, instance=tasklist)
	if form.is_valid():
		form.save()
		notify_webhook('tasklist', tasklist.id)
		if project:
			return redirect('project_detail', project_id=tasklist.project.id)
		else:
			return redirect('tasklist_manage')

	return render(request, 'projects/tasklist_edit.html', {'form': form, 'project': project, 'tasklist': tasklist, 'add_or_edit': add_or_edit})

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
		add_or_edit = 'Edit'
	else:
		link = Link()
		add_or_edit = 'Add'
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
	
	return render(request, 'projects/link_edit.html', {'form': form, 'link': link, 'add_or_edit': add_or_edit})

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
		project_id = project.id
		acctName = project.acctName
		return_url = reverse('project_detail', kwargs={'project_id': object_id})
	if parent_type == 'T':
		task = get_object_or_404(Task, pk=object_id)
		project_id = task.tasklist.project.id
		acctName = task.tasklist.project.acctName
		return_url = reverse('task_detail', kwargs={'tasklist_id': task.tasklist.id, 'task_id': object_id})
	if parent_type == 'R':
		risk = get_object_or_404(Risk, pk=object_id)
		project_id = risk.project.id
		acctName = risk.project.acctName
		return_url = reverse('risk_detail', kwargs={'risk_id': object_id})
	if parent_type == 'L':
		link = get_object_or_404(Link, pk=object_id)
		project_id = link.project.id
		acctName = link.project.acctName
		return_url = reverse('link_detail', kwargs={'project_id': link.project.id, 'link_id': object_id})
	if comment_id:
		comment = get_object_or_404(Comment, pk=comment_id)
		add_or_edit = 'Edit'
	else:
		comment = Comment()
		add_or_edit = 'Add'
	comment.type_of_comment = parent_type
	form = CommentForm(request.POST or None, instance=comment, parent_object=parent_type)
	if form.is_valid():
		form.save()
		if parent_type == 'P':
			comment.project = project
		if parent_type == 'T':
			comment.task = task
		if parent_type == 'R':
			comment.risk = risk
		if parent_type == 'L':
			comment.link = link
		comment.save()
		return redirect(return_url)

	return render(request, 'projects/comment_edit.html', {'form': form, 'add_or_edit': add_or_edit, 'project_id': project_id, 'acctName': acctName})

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
	return render(request, 'projects/comment_detail.html', {'comment': comment, 'project': project, 'task': task, 'risk': risk, 'link': link, 'object_type': object_type, 'object_id': object_id})

@login_required
def markdown_preview(request):
	if not request.is_ajax():
		return HttpResponseForbidden()
	text = request.POST.get('text', '')
	if text == '':
		return HttpResponse('')
	html = markdown.markdown(text)
	return HttpResponse(html)