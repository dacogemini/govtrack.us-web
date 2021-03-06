# Make pages more cachable by splitting user-specific parts of
# a page from anonymous parts.

from functools import wraps

from django.contrib.auth.models import AnonymousUser
from django.views.decorators.cache import cache_control
from django.conf import settings
import django.middleware.csrf

# Inject ourselves into CSRF processing to prevent the generation of CSRF
# tokens on anonymous views.
old_csrf_get_token = django.middleware.csrf.get_token
def new_csrf_get_token(request):
	if getattr(request, "anonymous", False):
		raise Exception("Requests marked 'anonymous' cannot generate CSRF tokens!")
	return old_csrf_get_token(request)
django.middleware.csrf.get_token = new_csrf_get_token

def anonymous_view(view):
	"""Marks a view as an anonymous, meaning this view returns nothing specific
	to the logged in user. In order to enforce this, the user, session, and COOKIES
	attributes of the request are cleared along with some keys in META.
	Additionally it sets cache-control settings on the output of the page and sets
	request.anonymous = True, which can be used in templates."""
	cache_control_args = { "public": True }
	if hasattr(view, "max_age"): cache_control_args["max_age"] = view.max_age
	view = cache_control(**cache_control_args)(view)
	@wraps(view)
	def g(request, *args, **kwargs):
		request.anonymous = True
		request.COOKIES = { }
		request.user = AnonymousUser()
		if hasattr(request, "session"): request.session = { }

		for header in list(request.META.keys()):
			if header not in (
					'SERVER_NAME', 'SERVER_PORT', 'HTTPS', 'wsgi.url_scheme', 'SERVER_PROTOCOL', 'HTTP_HOST',
					'REQUEST_METHOD', 'REQUEST_URI', 'DOCUMENT_URI', 'PATH_INFO', 'QUERY_STRING', 'CONTENT_LENGTH', 'CONTENT_TYPE',
					'REMOTE_ADDR'):
				del request.META[header]
				
		# In order for the Django debug template context processor to work, we can't
		# clear REMOTE_ADDR. Clear it if {{debug}} would be false. The resulting page
		# should not be cached since it may depend on REMOTE_ADDR.
		if 'REMOTE_ADDR' in request.META and (not settings.DEBUG or request.META['REMOTE_ADDR'] not in settings.INTERNAL_IPS):
			del request.META['REMOTE_ADDR']
			
		response = view(request, *args, **kwargs)
		response.csrf_processing_done = True # prevent generation of CSRF cookies
		return response
	return g
		
def user_view_for(anon_view_func):
	"""Marks a view as providing user-specific information for a view that the
	anonymous_view decorator has been applied to."""
	def decorator(view):
		anon_view_func.user_func = view
		return view
	return decorator

