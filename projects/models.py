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

from rest_framework.authtoken.models import Token

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

class Project(models.Model):
	"""
	The actual project.
	"""
	created = models.DateField(auto_now_add=True)
	acctName = models.CharField(max_length=30)
	category = models.ForeignKey(Category)
	PM = models.ForeignKey(User)
	AM = models.CharField(max_length=30, blank=True, null=True)
	startDate = models.DateField(blank=True, null=True)
	endDate = models.DateField(blank=True, null=True)
	isCompleted = models.BooleanField()
	completedDate = models.DateField(blank=True, null=True)
	isArchived = models.BooleanField()
	isDeleted = models.BooleanField()

	class Meta:
		ordering = ["acctName"]

	def __unicode__(self):
		return "%s (%s)" % (self.acctName, self.category)

class TaskList(models.Model):
	"""
	A list of tasks.
	"""
	created = models.DateField(auto_now_add=True)
	name = models.CharField(max_length=50)
	description = models.CharField(max_length=200, blank=True, null=True)
	isTemplate = models.BooleanField()
	project = models.ForeignKey(Project, blank=True, null=True)
	isDeleted = models.BooleanField()

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
	name = models.CharField(max_length=50)
	PM = models.ForeignKey(User, blank=True, null=True)
	startDate = models.DateField(blank=True, null=True)
	endDate = models.DateField(blank=True, null=True)
	dueDate = models.DateField(blank=True, null=True)
	description = models.TextField()
	isCompleted = models.BooleanField()
	completedDate = models.DateField(blank=True, null=True)

	def __unicode__(self):
		return "%s (%s)" % (self.name, self.tasklist)

	@property
	def is_past_due(self):
	    if (not self.isCompleted) and (timezone.now().date() > self.dueDate):
	    	return True
	    return False
	
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
		return "%s (%s)" % (self.description, self.project)

# Ensures API auth token is created for each user upon User creation
@receiver(post_save, sender=get_user_model())
def create_auth_token(sender, instance=None, created=False, **kwargs):
	if created:
		Token.objects.create(user=instance)
