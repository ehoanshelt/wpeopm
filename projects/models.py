import hashlib
import random
import string

from django.contrib.auth.models import User
from django.db import models

# Create your models here.
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
	created = models.DateField()
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
	created = models.DateField()
	name = models.CharField(max_length=50)
	description = models.CharField(max_length=200, blank=True, null=True)
	isTemplate = models.BooleanField()
	project = models.ForeignKey(Project, blank=True, null=True)

	def __unicode__(self):
		if self.project:
			return "%s (%s)" % (self.name, self.project)
		else:
			return "%s (Template)" % (self.name)

class Task(models.Model):
	"""
	Tasks for each project.
	"""
	created = models.DateField()
	tasklist = models.ForeignKey(TaskList)
	name = models.CharField(max_length=50)
	PM = models.ForeignKey(User)
	startDate = models.DateField(blank=True, null=True)
	endDate = models.DateField(blank=True, null=True)
	dueDate = models.DateField(blank=True, null=True)
	description = models.TextField()
	isCompleted = models.BooleanField()
	completedDate = models.DateField(blank=True, null=True)

	def __unicode__(self):
		return "%s (%s)" % (self.name, self.tasklist)

class Risk(models.Model):
	"""
	Risks associated with the project.
	"""
	created = models.DateField()
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
	created = models.DateField()
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
	created = models.DateField()
	description = models.TextField()
	project = models.ForeignKey(Project, blank=True, null=True)
	task = models.ForeignKey(Task, blank=True, null=True)
	risk = models.ForeignKey(Risk, blank=True, null=True)
	link = models.ForeignKey(Link, blank=True, null=True)
	attachment = models.FileField(upload_to='uploads', blank=True, null=True)

	def __unicode__(self):
		return "%s (%s)" % (self.description, self.project)

class APIUser(models.Model):
	"""
	Extends the contrib.auth.User model via one-to-one relationship.

	docs.djangoproject.com/en/1.6/topics/auth/customizing
	"""
	user = models.OneToOneField(User)
	APIKey = models.CharField(max_length=100)

	def generateAPIKey(self):
		"""
		Generates and returns an API key, stores the hash value in self.APIKey

		stackoverflow.com/questions/2257441
		stackoverflow.com/questions/5297448

		"""
		size = 15 # unrelated to max_length of APIKey, which will store a hash
		chars = string.ascii_letters + string.digits # choose from uppercase/lowercase letters and 0-9
		key = ''.join(random.choice(chars) for _ in range(size))
		self.APIKey = hashlib.md5(key).hexdigest() # md5 encode
		self.save()
		return key