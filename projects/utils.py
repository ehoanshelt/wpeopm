import logging
import requests
import time

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
	r = requests.post(URL, data=data)
