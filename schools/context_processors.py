import common.util as cm_util


def user_school_permissions(request):
    response = {
        'is_school_manager': cm_util.is_school_manager(request, request.resolver_match.kwargs),
        'is_school_teacher': cm_util.is_school_teacher(request, request.resolver_match.kwargs),
        'is_group_manager' : cm_util.is_group_manager(request, request.resolver_match.kwargs),
    }
    return response
