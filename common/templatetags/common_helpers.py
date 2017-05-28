# -*- coding: utf-8 -*-
from django import template
from django.template.defaultfilters import stringfilter
from itertools import chain
from datetime import datetime
from markdown2 import markdown
import re
import json
import ast

from common.models import (
    Manager,
    Teacher,
    School,
    SurveyResult,
    Notification,
)
from common.util import is_school_teacher

register = template.Library()


@register.filter
def literal_eval(value):
    try:
        return ast.literal_eval(value)
    except:
        return None


@register.filter
@stringfilter
def md(value):
    return markdown(value)


register.filter('md', md)


@stringfilter
def parse_date(date_string, format):
    """
    Return a datetime corresponding to date_string, parsed according to format.

    For example, to re-display a date string in another format::

        {{ "01/01/1970"|parse_date:"%Y-%m-%d"|date:"d-m-y }}

    """
    try:
        return datetime.strptime(date_string, format)
    except ValueError:
        return None


register.filter(parse_date)


@register.filter
def get_item(dictionary, key):
    try:
        return dictionary.get(key)
    except:
        return None


@register.filter
def get_json(text):
    try:
        return json.loads(text)
    except Exception as e:
        return {}


@register.filter
def jsonify(object):
    try:
        return json.dumps(object)
    except:
        return ''


@register.filter
def get_graph(text):
    try:
        return json.loads(text)
    except Exception as e:
        return {}


@register.filter
def split(value, arg):
    return value.split(arg)


def get_current_school(context):
    r = 'skoli\/(?P<school_id>[\d]*)'
    m = re.search(r, context.request.path)
    return m.group('school_id')


@register.inclusion_tag('common/_school_list.html', takes_context=True)
def get_user_schools(context):
    try:
        user = context['request'].user
        manager_schools = School.objects.filter(managers=Manager.objects.filter(user=user))
        teacher_schools = School.objects.filter(teachers=Teacher.objects.filter(user=user))
        schools = list(set(chain(manager_schools, teacher_schools)))
        return {'schools': schools}
    except:
        return {'schools': []}


@register.simple_tag(takes_context=True)
def get_school_name(context):
    r = 'skoli\/(?P<school_id>[\d]*)'
    m = re.search(r, context.request.path)
    try:
        return School.objects.get(pk=m.group('school_id')).name
    except:
        return "Skóli"


@register.assignment_tag
def get_survey_results(student, survey):
    sr = SurveyResult.objects.filter(survey=survey, student=student)
    if sr:
        return sr.first()
    return []
