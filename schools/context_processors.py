from django.template import RequestContext
from .util import *

def user_school_permissions(request):
    response = {
		'is_school_manager': is_school_manager(request, request.resolver_match.kwargs),
		'is_school_teacher': is_school_teacher(request, request.resolver_match.kwargs),
		'is_group_manager' : is_group_manager(request, request.resolver_match.kwargs),
    }
    return response