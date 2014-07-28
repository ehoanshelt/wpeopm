from django import forms

from projects.models import Category, Project, TaskList, Task, Link, Comment

class ProjectForm(forms.ModelForm):

	def clean_endDate(self):
		"""
		Validates that the end date is not before the start date.
		"""
		if self.cleaned_data['endDate']:
			if self.cleaned_data['startDate']:
				if self.cleaned_data['startDate'] > self.cleaned_data['endDate']:
					raise forms.ValidationError("Start date cannot be after end date.")
		return self.cleaned_data['endDate']

	category = forms.ModelChoiceField(Category.objects.all(), empty_label=None)
		
	startDate = forms.DateField(input_formats=('%m/%d/%Y', '%m-%d-%y',), required=False)
	endDate = forms.DateField(input_formats=('%m/%d/%Y', '%m-%d-%y',), required=False)
	completedDate = forms.DateField(input_formats=('%m/%d/%Y', '%m-%d-%y',), required=False)
	customerLaunchDate = forms.DateField(input_formats=('%m/%d/%Y', '%m-%d-%y',), required=False)

	class Meta:
		model = Project
		exclude = ['created',]

class TaskListForm(forms.ModelForm):

	class Meta:
		model = TaskList
		exclude = ['created', 'project', 'isTemplate', 'isDeleted',]

class TaskForm(forms.ModelForm):

	def clean_endDate(self):
		"""
		Validates that the end date is not before the start date.
		"""
		if self.cleaned_data['endDate']:
			if self.cleaned_data['startDate']:
				if self.cleaned_data['startDate'] > self.cleaned_data['endDate']:
					raise forms.ValidationError("Start date cannot be after end date.")
		return self.cleaned_data['endDate']
		
	startDate = forms.DateField(input_formats=('%m/%d/%Y', '%m-%d-%y',), required=False)
	endDate = forms.DateField(input_formats=('%m/%d/%Y', '%m-%d-%y',), required=False)
	completedDate = forms.DateField(input_formats=('%m/%d/%Y', '%m-%d-%y',), required=False)

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
