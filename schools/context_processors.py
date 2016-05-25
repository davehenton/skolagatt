from django.template import RequestContext

def user_school_permissions(request):
    print(request.user)
    r = {
        'is_school_manager': True,
        'is_school_teacher': True,
        'is_group_manager': True,
    }
    return r