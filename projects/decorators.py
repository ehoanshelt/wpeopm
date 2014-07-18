from django.conf import settings
from django.http import HttpResponseRedirect

def secure_required(view_func):
	"""
	Decorator makes sure URL is accessed over https.
	"""
	def _wrapped_view_func(request, *args, **kwargs):
		if not request.is_secure():
			if getattr(settings, 'HTTPS_SUPPORT', True):
				request_url = request.build_absolute_uri(request.get_full_path())
				secure_url_protocol = request_url.replace('http://', 'https://')
				secure_url = secure_url_protocol.replace(':8000', ':8443')
				return HttpResponseRedirect(secure_url)
		return view_func(request, *args, **kwargs)
	return _wrapped_view_func