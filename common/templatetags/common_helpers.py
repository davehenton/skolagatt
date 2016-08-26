# -*- coding: utf-8 -*-
from django import template
from django.template.defaultfilters import stringfilter
from common.models import Manager, Teacher, School, SurveyResult
from itertools import chain
from datetime import datetime
import re, json
from markdown2 import markdown

from schools.util import *

register = template.Library()

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
	return dictionary.get(key)

@register.filter
def get_json(text):
	try:
		return json.loads(text)
	except Exception as e:
		return {}

@register.filter
def get_graph(text):
	try:
		return json.loads(text)
	except Exception as e:
		return {}

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

@register.inclusion_tag('common/_message_list.html', takes_context=True)
def get_user_messages(context, **kwargs):
	try:
		user = context['request'].user
		manager_schools = School.objects.filter(managers=Manager.objects.filter(user=user))
		teacher_schools = School.objects.filter(teachers=Teacher.objects.filter(user=user))
		schools = list(set(chain(manager_schools, teacher_schools)))

		messages = []
		all_messages = get_messages()
		for message in all_messages:
			if message['file'] != None:
				file_name = message['file'].split('/')[-1]
				file_name = file_name.encode('utf-8')
				message['file_name'] = file_name
			messages.append(message)

		if is_school_teacher(context['request'], kwargs):
			context['messages'] = [message for message in messages if message['teachers_allow'] == True]
		else:
			context['messages'] = messages

		return {'messages': messages}
	except Exception as e:
		return {'messages': []}

@register.simple_tag(takes_context=True)
def get_nr_notifications(context, messages):
	message_ids = [m['pk'] for m in messages]
	n = Notification.objects.filter(user=context.request.user).filter(notification_type='message').filter(notification_id__in=message_ids)
	return len(messages) - len(n)

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