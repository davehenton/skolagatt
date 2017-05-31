# -*- coding: utf-8 -*-
from django.utils.text import slugify
from django.core.cache import cache
from django.core.exceptions import ObjectDoesNotExist

from celery.task.control import inspect

from celery.contrib.abortable import AbortableAsyncResult

from uuid import uuid4

import common.models as cm_models


class NotLoggedIn(Exception):
    pass


class IsSuperUser(Exception):
    pass


def get_current_school(path_variables):
    if 'school_id' in path_variables:
        return path_variables['school_id']
    elif 'pk' in path_variables:
        return path_variables['pk']
    return None


def login_check(request):
    if not request.user.is_authenticated:
        raise NotLoggedIn
    if request.user.is_superuser:
        raise IsSuperUser


def _is_school_manager(request, kwargs):
    school_id = get_current_school(kwargs)

    if school_id and cm_models.School.objects.filter(
        pk=school_id,
        managers=cm_models.Manager.objects.filter(user=request.user)
    ):
        return True

    return False


def is_school_manager(request, kwargs):
    try:
        login_check(request)
    except NotLoggedIn:
        return False
    except IsSuperUser:
        return True

    return _is_school_manager(request, kwargs)


def is_manager(request):
    try:
        login_check(request)
    except NotLoggedIn:
        return False
    except IsSuperUser:
        return True

    return cm_models.Manager.objects.filter(user=request.user).exists()


def is_school_teacher(request, kwargs):
    try:
        login_check(request)
    except NotLoggedIn:
        return False
    except IsSuperUser:
        return True

    if _is_school_manager(request, kwargs):
        return True

    school_id = get_current_school(kwargs)
    teacher = cm_models.Teacher.objects.filter(user=request.user).first()
    school = cm_models.School.objects.filter(pk=school_id, teachers=teacher)
    if school.exists():
        return True
    return False


def is_teacher(request):
    try:
        login_check(request)
    except NotLoggedIn:
        return False
    except IsSuperUser:
        return True

    return cm_models.Teacher.objects.filter(user=request.user).exists()


def _find_studentgroup_id(request, kwargs):
    if 'student_group' in kwargs:
        return kwargs['student_group']
    elif 'studentgroup_id' in kwargs:
        return kwargs['studentgroup_id']
    elif 'bekkur' in request.path and 'pk' in kwargs:
        return kwargs['pk']
    return None


def _get_studentgroup_id_via_groupsurvey_id(groupsurvey_id):
    try:
        groupsurvey = cm_models.GroupSurvey.objects.get(pk=groupsurvey_id)
        studentgroup = groupsurvey.studentgroup
        if studentgroup:
            return studentgroup.id
    except ObjectDoesNotExist:
        return None
    return None


def _find_studentgroup_id_via_groupsurvey(request, kwargs):
    groupsurvey_id = None
    if 'survey_id' in kwargs:
        groupsurvey_id = kwargs['survey_id']
    elif 'próf' in request.path and 'pk' in kwargs:
        groupsurvey_id = kwargs['pk']

    return _get_studentgroup_id_via_groupsurvey_id(groupsurvey_id)


def _find_studentgroup_id_via_student(request, kwargs):
    if 'nemandi' in request.path and 'pk' in kwargs:
        studentgroup = cm_models.StudentGroup.objects.filter(students=kwargs['pk'])
        if studentgroup.exists():
            return studentgroup.first().id
    return None


def get_studentgroup_id(request, kwargs):
    studentgroup_id = _find_studentgroup_id(request, kwargs)
    if studentgroup_id:
        return studentgroup_id
    studentgroup_id = _find_studentgroup_id_via_groupsurvey(request, kwargs)
    if studentgroup_id:
        return studentgroup_id
    studentgroup_id = _find_studentgroup_id_via_student(request, kwargs)
    if studentgroup_id:
        return studentgroup_id
    return None


def is_group_manager(request, kwargs):
    try:
        login_check(request)
    except NotLoggedIn:
        return False
    except IsSuperUser:
        return True

    studentgroup_id = get_studentgroup_id(request, kwargs)

    return cm_models.StudentGroup.objects.filter(
        pk=studentgroup_id,
        group_managers=cm_models.Teacher.objects.filter(user=request.user)
    ).exists()


def get_groupsurvey_id(kwargs):
    groupsurvey_id = None

    if 'groupsurvey_id' in kwargs:
        groupsurvey_id = kwargs['groupsurvey_id']
    elif 'survey_id' in kwargs:
        groupsurvey_id = kwargs['survey_id']
    elif 'pk' in kwargs:
        groupsurvey_id = kwargs['pk']

    return groupsurvey_id


def groupsurvey_is_open(request, kwargs):
    try:
        login_check(request)
    except NotLoggedIn:
        return False
    except IsSuperUser:
        return True

    groupsurvey_id = get_groupsurvey_id(kwargs)

    groupsurvey = cm_models.GroupSurvey.objects.filter(pk=groupsurvey_id)
    if groupsurvey.exists():
        return groupsurvey.first().is_open()

    return False


def slug_sort(q, attr):
    return sorted(q, key=lambda x: slugify(getattr(x, attr)))


def add_field_classes(obj, field_list, cssdef={'class': 'form-control'}):
    ''' To add form-control class to form fields '''
    for item in field_list:
        obj.fields[item].widget.attrs.update(cssdef)


def store_import_data(request, slug, data):
    """Store data in cache, and store the cache id in current session"""

    cache_id = str(uuid4())
    # Remove 'error' keys from dict list
    remove_keys = ['error']
    clean_data = list(map(lambda x: {k: v for k, v in x.items() if k not in remove_keys}, data))
    cache.set(cache_id, clean_data, 15 * 60)  # Store for max 15 minutes
    request.session[slug] = cache_id

    return cache_id


def get_import_data(request, slug):
    """Get data from cache using id from session store"""
    cache_id = request.session[slug]
    del(request.session[slug])
    data = cache.get(cache_id)
    cache.delete(cache_id)
    return data


def cancel_import_data(request, slug):
    """Delete data from cache using id from session store, delete id from session store"""
    cache_id = request.session[slug]
    del(request.session[slug])
    cache.delete(cache_id)


def get_celery_jobs(job_name):
    jobs = []
    active_celery_tasks = inspect().active()
    if active_celery_tasks:
        for k in active_celery_tasks.keys():
            host_tasks = active_celery_tasks[k]
            for host_task in host_tasks:
                if host_task.get('name') == job_name:
                    jobs.append(host_task.get('id'))
    return jobs


def abort_celery_job(job_id):
    job = AbortableAsyncResult(job_id)
    if job:
        return job.abort()
