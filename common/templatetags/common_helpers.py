from django import template
from common.models import Manager, Teacher, School
from itertools import chain
import re

register = template.Library()

@register.inclusion_tag('common/_school_list.html', takes_context=True)
def get_user_schools(context):
	user = context['request'].user
	manager_schools = School.objects.filter(managers=Manager.objects.filter(ssn=user.username))
	teacher_schools = School.objects.filter(teachers=Teacher.objects.filter(ssn=user.username))
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