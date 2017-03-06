import common.util as cm_util


def user_school_permissions(request):
    #import pdb; pdb.set_trace()
    kwargs = request.resolver_match.kwargs if request.resolver_match else {}
    response = {
        'is_school_manager': cm_util.is_school_manager(request, kwargs),
        'is_school_teacher': cm_util.is_school_teacher(request, kwargs),
        'is_group_manager' : cm_util.is_group_manager(request, kwargs),
    }
    return response
