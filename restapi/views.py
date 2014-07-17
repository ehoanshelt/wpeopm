from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser

from projects.models import Link
from restapi.serializers import LinkSerializer

class JSONResponse(HttpResponse):
	"""
	An HttpResponse that renders its content into JSON.
	"""
	def __init__(self, data, **kwargs):
		content = JSONRenderer().render(data)
		kwargs['content_type'] = 'application/json'
		super(JSONResponse, self).__init__(content, **kwargs)

@csrf_exempt
def link_list(request):
	"""
	List all links, or create a new link.
	"""
	if request.method == 'GET':
		links = Link.objects.all()
		serializer = LinkSerializer(links, many=True)
		return JSONResponse(serializer.data)

	elif request.method == 'POST':
		data = JSONParser().parse(request)
		serializer = LinkSerializer(data=data)
		if serializer.is_valid():
			serializer.save()
			return JSONResponse(serializer.data, status=201)
		return JSONResponse(serializer.errors, status=400)

@csrf_exempt
def link_detail(request, pk):
	"""
	Retrieve, update, or delete a link.
	"""
	try:
		link = Link.objects.get(pk=pk)
	except Link.DoesNotExist:
		return HttpResponse(status=404)

	if request.method == 'GET':
		serializer = LinkSerializer(link)
		return JSONResponse(serializer.data)

	elif request.method == 'PUT':
		data = JSONParser().parse(request)
		serializer = LinkSerializer(link, data=data)
		if serializer.is_valid():
			serializer.save()
			return JSONResponse(serializer.data)
		return JSONResponse(serializer.errors, status=400)

	elif request.method == 'DELETE':
		link.delete()
		return HttpResponse(status=204)
