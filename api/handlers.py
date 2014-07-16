from piston.handler import BaseHandler

from projects.models import *

class ProjectsHandler(BaseHandler):
	"""
	Returns projects.
	"""
	allowed_methods = ('GET',)
	model = Project
	fields = ('id', 'created', 'acctName', 'category', 'PM', 'AM', 'startDate', 'endDate', 'isCompleted', 'completedDate', 'isArchived', 'isDeleted', 'tasklists', 'tasks')

	@classmethod
	def id(cls, model):
		return model.id

	@classmethod
	def created(cls, model):
		return model.created

	@classmethod
	def acctName(cls, model):
		return model.acctName

	@classmethod
	def category(cls, model):
		return model.category.name

	@classmethod
	def PM(cls, model):
		return model.PM.username

	@classmethod
	def AM(cls, model):
		return model.AM

	@classmethod
	def startDate(cls, model):
		return model.startDate

	@classmethod
	def endDate(cls, model):
		return model.endDate

	@classmethod
	def isCompleted(cls, model):
		return model.isCompleted

	@classmethod
	def completedDate(cls, model):
		return model.completedDate

	@classmethod
	def isArchived(cls, model):
		return model.isArchived

	@classmethod
	def isDeleted(cls, model):
		return model.isDeleted

	@classmethod
	def tasklists(cls, model):
		tasklist = TaskList.objects.filter(project=model)
		return list(tasklist)

	@classmethod
	def tasks(cls, model):
		tasks = Task.objects.filter(tasklist__project=model)
		return list(tasks)

	def read(self, request):
		"""
		Handles the processing of the API call.
		Filters are passed via query string parameter.
		Valid filters are:
			[currently none]
		"""
		projects = Project.objects.all()
		project_list = list(projects)

		return project_list