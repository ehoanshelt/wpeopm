from django import forms

from projects.models import Project, TaskList, Task, Link, Comment

class ProjectForm(forms.ModelForm):

	class Meta:
		model = Project
		exclude = ['created',]

class TaskListForm(forms.ModelForm):

	class Meta:
		model = TaskList
		exclude = ['created', 'project', 'isTemplate', 'isDeleted',]

class TaskForm(forms.ModelForm):

	class Meta:
		model = Task

class LinkForm(forms.ModelForm):

	class Meta:
		model = Link
		exclude = ['project',]

class CommentForm(forms.ModelForm):

	def __init__(self, *args, **kwargs):
		parent_object = kwargs.pop('parent_object')
		super(forms.ModelForm, self).__init__(*args, **kwargs)
		self.fields.pop('type_of_comment')
		if parent_object == 'P':
			self.fields.pop('task')
			self.fields.pop('risk')
			self.fields.pop('link')
		if parent_object == 'T':
			self.fields.pop('project')
			self.fields.pop('risk')
			self.fields.pop('link')
		if parent_object == 'R':
			self.fields.pop('project')
			self.fields.pop('task')
			self.fields.pop('link')
		if parent_object == 'L':
			self.fields.pop('project')
			self.fields.pop('task')
			self.fields.pop('risk')

	class Meta:
		model = Comment
