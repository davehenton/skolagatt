# -*- coding: utf-8 -*-
from django import template
from common.models import Manager, Teacher, School, SurveyResult
from itertools import chain
import re, json

register = template.Library()

@register.filter
def get_item(dictionary, key):
	return dictionary.get(key)

@register.filter
def get_json(text):
	try:
		return json.loads(text)
	except:
		return {}

@register.inclusion_tag('common/_school_list.html', takes_context=True)
def get_user_schools(context):
	user = context['request'].user
	manager_schools = School.objects.filter(managers=Manager.objects.filter(user=user))
	teacher_schools = School.objects.filter(teachers=Teacher.objects.filter(user=user))
	schools = list(set(chain(manager_schools, teacher_schools)))
	return {'schools': schools}

@register.simple_tag(takes_context=True)
def get_school_name(context):
	r = 'skoli\/(?P<school_id>[\d]*)'
	m = re.search(r, context.request.path)
	try:
		return School.objects.get(pk=m.group('school_id')).name
	except:
		return "Velja skóla"

@register.assignment_tag
def get_survey_results(student, survey):
	sr=SurveyResult.objects.filter(survey=survey, student=student)
	if sr:
		return sr.first()
	return []