import datetime
import hashlib
import random
import string

from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

class GetOrNoneManager(models.Manager):
	"""
	Adds get_or_none method to objects
	"""
	def get_or_none(self, **kwargs):
		try:
			return self.get(**kwargs)
		except self.model.DoesNotExist:
			return None

class Category(models.Model):
	"""
	The Category that Projects have.
	e.g. "On Hold", "Internal", "Onboarding", etc.
	"""
	name = models.CharField(max_length=30)

	class Meta:
		ordering = ["name"]
		verbose_name_plural = "categories"

	def __unicode__(self):
		return self.name

STATUS_CHOICES = (
	('N', 'Not Started'),
	('I', 'In Progress'),
	('C', 'Complete'),
)

DEFAULT_STATUS_CHOICE = 'N'

HANDOFF_CHOICES = (
	('N', 'No Handoff'),
	('C', 'Cold Handoff'),
	('W', 'Warm Handoff'),
)

DEFAULT_HANDOFF_CHOICE = 'N'

class Project(models.Model):
	"""
	The actual project.
	"""
	created = models.DateField(auto_now_add=True)
	acctName = models.CharField(max_length=30, default="New Project")
	category = models.ForeignKey(Category)
	PM = models.ForeignKey(User)
	AM = models.CharField(max_length=30, blank=True, null=True)
	startDate = models.DateField(blank=True, null=True)
	endDate = models.DateField(blank=True, null=True)
	completedDate = models.DateField(blank=True, null=True)
	isArchived = models.BooleanField(default=False)
	isDeleted = models.BooleanField(default=False)
	customerLaunchDate = models.DateField(blank=True, null=True)
	status = models.CharField(max_length=1, choices=STATUS_CHOICES, default=DEFAULT_STATUS_CHOICE)
	handoffType = models.CharField(max_length=1, choices=HANDOFF_CHOICES, default=DEFAULT_HANDOFF_CHOICE)
	destPod = models.CharField(max_length=6, blank=True, null=True)

	objects = GetOrNoneManager()

	class Meta:
		ordering = ["acctName"]

	@property
	def lastTicketResponseDate(self):
		"""
		Queries ZenDesk to get the last response date for a ticket with the sitename associated with self.acctName.
		Used to measure customer engagement.
		"""
		return timezone.now()
		# placeholder - today

	@property
	def recentLastTicketResponseDate(self):
		"""
		Returns True if the last ticket response date is within two days ago.
		"""
		return (self.lastTicketResponseDate < (timezone.now() - datetime.timedelta(days=2)))

	@property
	def otherTickets(self):
		"""
		Queries ZenDesk to get the number of tickets the customer has submitted. Generally if the customer is engaging Support
		instead of Onboarding, they should be funneled back into the Onboarding queue.
		"""
		return 2
		# placeholder - the customer has the handoff ticket plus the initial inquiry ticket

	@property
	def riskScore(self):
		"""
		Looks at the following conditions:
		** Customer has not responded to a ticket in the past two days
		** Customer has more than two tickets open in ZenDesk
		** Customer has not provided a launch date

		The more conditions are True, the more the customer needs attention

		See http://stackoverflow.com/questions/12765833/ for a code explanation
		"""
		conditions = [
			(self.recentLastTicketResponseDate),
			(self.otherTickets > 2),
			(self.customerLaunchDate is None)
		]
		return len(conditions) - sum(bool(x) for x in conditions) # returns 0..n..len(conditions)

	def __unicode__(self):
		return "%s (%s)" % (self.acctName, self.category)

class TaskList(models.Model):
	"""
	A list of tasks.
	"""
	created = models.DateField(auto_now_add=True)
	name = models.CharField(max_length=50, default='New Task List')
	description = models.CharField(max_length=200, blank=True, null=True)
	isTemplate = models.BooleanField(default=False)
	project = models.ForeignKey(Project, blank=True, null=True)
	isDeleted = models.BooleanField(default=False)

	def __unicode__(self):
		if self.project:
			return "%s (%s)" % (self.name, self.project)
		else:
			return "%s (Template)" % (self.name)

class Task(models.Model):
	"""
	Tasks for each project.
	"""
	created = models.DateField(auto_now_add=True)
	tasklist = models.ForeignKey(TaskList)
	name = models.CharField(max_length=50, default='New Task')
	PM = models.ForeignKey(User, blank=True, null=True)
	startDate = models.DateField(blank=True, null=True)
	endDate = models.DateField(blank=True, null=True)
	dueDate = models.DateField(blank=True, null=True)
	description = models.TextField(default='New Task')
	completedDate = models.DateField(blank=True, null=True)
	status = models.CharField(max_length=1, choices=STATUS_CHOICES, default=DEFAULT_STATUS_CHOICE)

	def __unicode__(self):
		return "%s (%s)" % (self.name, self.tasklist)

	@property
	def is_past_due(self):
		if self.dueDate:
		    if (not self.isCompleted) and (timezone.now().date() > self.dueDate):
		    	return True
		return False

	@property
	def can_be_completed(self):
		"""
		Returns True if all of the tasks this task depends on are completed.
		"""
		dependencies = self.task_set.all()
		for d in dependencies:
			if not d.dependsOn.status == 'C':
				return False
		return True

	@property
	def has_dependencies(self):
		"""
		Returns True if there are any Dependency.task objects that have this as a key.
		"""
		return (len(Dependency.objects.filter(task=self)) > 0)

class Dependency(models.Model):
	"""
	Handles dependencies of tasks.
	"""
	task = models.ForeignKey(Task, related_name="task_set")
	dependsOn = models.ForeignKey(Task, related_name="dependency_set")

	objects = GetOrNoneManager()

	def __unicode__(self):
		return "%s depends on %s" % (self.task.name, self.dependsOn.name)

	class Meta:
		verbose_name_plural = "dependencies"

class Risk(models.Model):
	"""
	Risks associated with the project.
	"""
	created = models.DateField(auto_now_add=True)
	project = models.ForeignKey(Project)
	name = models.CharField(max_length=50)
	probability = models.IntegerField(default=5)
	impact = models.IntegerField(default=5)
	doesImpactCost = models.BooleanField()
	doesImpactSchedule = models.BooleanField()
	doesImpactPerformance = models.BooleanField()
	plan = models.TextField()

	def __unicode__(self):
		return "%s (%s)" % (self.name, self.project)

class Link(models.Model):
	"""
	Links associated with the project.
	"""
	created = models.DateField(auto_now_add=True)
	project = models.ForeignKey(Project)
	name = models.CharField(max_length=30)
	description = models.CharField(max_length=200, blank=True, null=True)
	code = models.CharField(max_length=255)

	def __unicode__(self):
		return "%s (%s)" % (self.name, self.project)

COMMENT_CHOICES = (
	('P', 'Project'),
	('T', 'Task'),
	('R', 'Risk'),
	('L', 'Link'),
)

class Comment(models.Model):
	"""
	Comments can be associated with Projects, Tasks, Risks, or Links.

	NOTE: I'm certain there is a better way to do this association.
	"""
	type_of_comment = models.CharField(max_length=1, choices=COMMENT_CHOICES)
	created = models.DateField(auto_now_add=True)
	description = models.TextField()
	project = models.ForeignKey(Project, blank=True, null=True)
	task = models.ForeignKey(Task, blank=True, null=True)
	risk = models.ForeignKey(Risk, blank=True, null=True)
	link = models.ForeignKey(Link, blank=True, null=True)
	attachment = models.FileField(upload_to='uploads', blank=True, null=True)

	def __unicode__(self):
		if self.type_of_comment == 'P':
			parent_name = self.project
		elif self.type_of_comment == 'T':
			parent_name = self.task
		elif self.type_of_comment == 'L':
			parent_name = self.link
		else:
			parent_name = ''
		return "%s (%s)" % (self.description, parent_name)
