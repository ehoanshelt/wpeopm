import datetime

from django.contrib.auth.models import User
from django.test import TestCase
from django.utils import timezone

from projects.forms import ProjectForm, TaskForm
from projects.models import Project, Category, Task, TaskList

class ProjectFormTests(TestCase):

	def setUp(self):
		"""
		Sets up the database and what-have-you.
		"""
		Category.objects.create(name='Test Category')
		User.objects.create(username='Test User', password='qwerty', date_joined=timezone.now())

	def test_end_date_before_start_date(self):
		"""
		Project should not have an end date before the start date.
		"""
		today = timezone.now().date()
		yesterday = today - datetime.timedelta(days=1)
		form_data = {'startDate': today, 'endDate': yesterday,
					'status': 'N', 'acctName': 'New Account', 
					'category': 1, 'PM': 1}
		form = ProjectForm(data=form_data)
		self.assertEqual(form.is_valid(), False)

	def test_end_date_equal_to_start_date(self):
		"""
		Project can have an end date equal to the start date.
		"""
		today = timezone.now().date()
		form_data = {'startDate': today, 'endDate': today,
					'status': 'N', 'acctName': 'New Account', 
					'category': 1, 'PM': 1}
		form = ProjectForm(data=form_data)
		self.assertEqual(form.is_valid(), True)

	def test_end_date_after_start_date(self):
		"""
		Project can have an end date after the start date.
		"""
		today = timezone.now().date()
		tomorrow = today + datetime.timedelta(days=1)
		form_data = {'startDate': today, 'endDate': tomorrow,
					'status': 'N', 'acctName': 'New Account', 
					'category': 1, 'PM': 1}
		form = ProjectForm(data=form_data)
		self.assertEqual(form.is_valid(), True)

class TaskFormTests(TestCase):

	def setUp(self):
		"""
		Sets up the database and what-have-you.
		"""
		Category.objects.create(name='Test Category')
		User.objects.create(username='Test User', password='qwerty', date_joined=timezone.now())
		TaskList.objects.create(name='Test Task List', description='This is a test task list.')

	def test_end_date_before_start_date(self):
		"""
		Task should not have an end date before the start date.
		"""
		today = timezone.now().date()
		yesterday = today - datetime.timedelta(days=1)
		form_data = {'startDate': today, 'endDate': yesterday,
					'tasklist': 1, 'name': 'New Task', 'description': 'New Task',
					'status': 'N', 'PM': 1}
		form = TaskForm(data=form_data)
		self.assertEqual(form.is_valid(), False)

	def test_end_date_equal_to_start_date(self):
		"""
		Task can have an end date equal to the start date.
		"""
		today = timezone.now().date()
		form_data = {'startDate': today, 'endDate': today,
					'tasklist': 1, 'name': 'New Task', 'description': 'New Task',
					'status': 'N', 'PM': 1}
		form = TaskForm(data=form_data)
		self.assertEqual(form.is_valid(), True)

	def test_end_date_after_start_date(self):
		"""
		Task can have an end date after the start date.
		"""
		today = timezone.now().date()
		tomorrow = today + datetime.timedelta(days=1)
		form_data = {'startDate': today, 'endDate': tomorrow,
					'tasklist': 1, 'name': 'New Task', 'description': 'New Task',
					'status': 'N', 'PM': 1}
		form = TaskForm(data=form_data)
		self.assertEqual(form.is_valid(), True)
