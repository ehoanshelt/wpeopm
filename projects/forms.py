from django import forms

from projects.models import Project, TaskList, Task, Link

class ProjectForm(forms.ModelForm):

	class Meta:
		model = Project

class TaskListForm(forms.ModelForm):

	class Meta:
		model = TaskList
		exclude = ['project',]

class TaskForm(forms.ModelForm):

	class Meta:
		model = Task

class LinkForm(forms.ModelForm):

	class Meta:
		model = Link
		exclude = ['project',]