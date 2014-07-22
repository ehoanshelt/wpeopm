from django.forms import widgets

from rest_framework import serializers

from projects.models import Project, Link, TaskList, Task

class ProjectSerializer(serializers.ModelSerializer):

	class Meta:
		model = Project
		fields = ('id', 'acctName', 'category', 'PM', 'AM', 'startDate', 'isCompleted', 'completedDate', 'isArchived', 'isDeleted')


class TaskListSerializer(serializers.ModelSerializer):

	class Meta:
		model = TaskList
		fields = ('id', 'name', 'description', 'project', 'isTemplate', 'isDeleted')

class TaskSerializer(serializers.ModelSerializer):

	class Meta:
		model = Task
		fields = ('id', 'tasklist', 'name', 'PM', 'startDate', 'endDate', 'dueDate', 'description', 'isCompleted', 'completedDate')
		depth = 3

class LinkSerializer(serializers.ModelSerializer):

	class Meta:
		model = Link
		fields = ('id', 'name', 'description', 'code', 'project')

