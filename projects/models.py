from django.contrib.auth import User
from django.db import models

# Create your models here.
class Project(models.Model):
	acctName: models.CharField(max_length=30)
	PM: models.ForeignKey(User)
	startDate: models.DateField()
	endDate: models.DateField()
	isArchived: models.BooleanField()
	isDeleted: models.BooleanField()

class Task(models.Model):
	project: models.ForeignKey(Project)
	name: models.CharField(max_length=50)
	PM: models.ForeignKey(User)
	startDate: models.DateField()
	endDate: models.DateField()
	description: models.TextField()

class Risk(models.Model):
	project: models.ForeignKey(Project)
	name: models.CharField(max_length=50)
	probability: models.IntegerField(default=5)
	impact: models.IntegerField(default=5)
	doesImpactCost: models.BooleanField()
	doesImpactSchedule: models.BooleanField()
	doesImpactPerformance: models.BooleanField()
	plan: models.TextField()

