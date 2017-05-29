# -*- coding: utf-8 -*-
from django.utils.text import slugify
from django.core.cache import cache
from django.core.exceptions import ObjectDoesNotExist

from celery.task.control import inspect

from celery.contrib.abortable import AbortableAsyncResult

from uuid import uuid4

import common.models as cm_models


def get_current_school(path_variables):
    if 'school_id' in path_variables:
        return path_variables['school_id']
    elif 'pk' in path_variables:
        return path_variables['pk']
    return None


def is_school_manager(request, kwargs):
    if not request.user.is_authenticated:
        return False
    elif request.user.is_superuser:
        return True

    try:
        school_id = get_current_school(kwargs)
        if school_id and cm_models.School.objects.filter(
            pk=school_id,
            managers=cm_models.Manager.objects.filter(user=request.user)
        ):
            return True
    except Exception as e:
        pass
    return False


def is_manager(request):
    if request.user.is_authenticated and cm_models.Manager.objects.filter(user=request.user):
        return True
    return False


def is_school_teacher(request, kwargs):
    if not request.user.is_authenticated:
        return False
    elif request.user.is_superuser:
        return True
    elif is_school_manager(request, kwargs):
        return True
    school_id = get_current_school(kwargs)
    teacher = cm_models.Teacher.objects.filter(user=request.user)
    if not teacher:
        return False
    if school_id:
        if cm_models.School.objects.filter(
            pk=school_id,
            teachers=teacher,
        ):
            return True
        else:
            return False
    elif teacher:
        return True
    return False


def is_teacher(request):
    if request.user.is_authenticated and cm_models.Teacher.objects.filter(user=request.user):
        return True

    return False


def is_group_manager(request, kwargs):
    if not request.user.is_authenticated:
        return False
    elif request.user.is_superuser:
        return True

    studentgroup_id = None

    try:
        if 'student_group' in kwargs:
            studentgroup_id = kwargs['student_group']
        elif 'studentgroup_id' in kwargs:
            studentgroup_id = kwargs['studentgroup_id']
        elif 'survey_id' in kwargs:
            studentgroup_id = cm_models.GroupSurvey.objects.get(
                pk=kwargs['survey_id']
            ).studentgroup.id
        elif 'próf' in request.path and 'pk' in kwargs:
            studentgroup_id = cm_models.GroupSurvey.objects.get(
                pk=kwargs['pk']
            ).studentgroup.id
        elif 'bekkur' in request.path and 'pk' in kwargs:
            studentgroup_id = kwargs['pk']
        elif 'nemandi' in request.path and 'pk' in kwargs:
            studentgroup_id = cm_models.StudentGroup.objects.filter(students=kwargs['pk']).id
    except (ObjectDoesNotExist, AttributeError):
        return False
    else:
        if studentgroup_id and cm_models.StudentGroup.objects.filter(
            pk=studentgroup_id,
            group_managers=cm_models.Teacher.objects.filter(user=request.user)
        ):
            return True
    return False


def groupsurvey_is_open(request, kwargs):
    if not request.user.is_authenticated:
        return False

    if request.user.is_superuser:
        return True

    groupsurvey_id = None

    try:
        if 'groupsurvey_id' in kwargs:
            groupsurvey_id = kwargs['groupsurvey_id']
        elif 'survey_id' in kwargs:
            groupsurvey_id = kwargs['survey_id']
        elif 'pk' in kwargs:
            groupsurvey_id = kwargs['pk']
    except (ObjectDoesNotExist, AttributeError):
        return False
    else:
        try:
            groupsurvey = cm_models.GroupSurvey.objects.get(pk=groupsurvey_id)
        except ObjectDoesNotExist:
            return False
        else:
            return groupsurvey.is_open()
    return False


def slug_sort(q, attr):
    return sorted(q, key=lambda x: slugify(getattr(x, attr)))


def add_field_classes(self, field_list, cssdef={'class': 'form-control'}):
    ''' To add form-control class to form fields '''
    for item in field_list:
        self.fields[item].widget.attrs.update(cssdef)


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
