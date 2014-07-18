from rest_framework import generics, permissions, viewsets

from projects.models import Project, Link, TaskList, Task
from restapi.serializers import ProjectSerializer, LinkSerializer, TaskListSerializer, TaskSerializer

class LinkViewSet(viewsets.ModelViewSet):
	"""
	API endpoint that allows links to be viewed or edited.
	"""
	queryset = Link.objects.all()
	serializer_class = LinkSerializer
	permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

class ProjectViewSet(viewsets.ModelViewSet):
	"""
	API endpoint that allows projects to be viewed or edited.
	"""
	queryset = Project.objects.all()
	serializer_class = ProjectSerializer
	permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

class TaskListViewSet(viewsets.ModelViewSet):
	"""
	API endpoint that allows task lists to be viewed or edited.
	"""
	queryset = TaskList.objects.all()
	serializer_class = TaskListSerializer
	permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

class TaskViewSet(viewsets.ModelViewSet):
	"""
	API endpoint that allows tasks to be viewed or edited.
	"""
	queryset = Task.objects.all()
	serializer_class = TaskSerializer
	permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
