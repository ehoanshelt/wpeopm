import json
import logging
import requests
import time

from django.http import HttpResponse

logger = logging.getLogger('webhook')

def notify_webhook(object_type, object_id):
	"""
	Sends a POST request to a webpage consisting of the object type, object id, and timestamp.
	"""
	URL = 'http://implementation.wpengine.com/web-hook'
	data = {
		'object_type': object_type,
		'object_id': object_id,
		'timestamp': int(time.time())
	}
	# uncomment below line for production
	#r = requests.post(URL, data=data)

def JsonHttpResponse(data):
	"""
	Wraps the HttpResponse method to make it easier to return JSON.

	Data passed to this method must be in a dictionary.
	"""
	json_data = json.dumps(data)
	return HttpResponse(json_data, mimetype="application/json")