from django import forms

from projects.models import Project, Task, Link

class ProjectForm(forms.ModelForm):

	class Meta:
		model = Project

class TaskForm(forms.ModelForm):

	class Meta:
		model = Task
		exclude = ['project',]

class LinkForm(forms.ModelForm):

	class Meta:
		model = Link
		exclude = ['project',]