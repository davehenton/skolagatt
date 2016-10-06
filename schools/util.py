from common.models import *
from django.conf import settings
from django.utils.text import slugify
import requests

def get_messages():
  """Get all messages from innrivefur"""
  try:
      r = requests.get(settings.INNRI_SKILABOD_URL+'&json_api_key='+settings.INNRI_SKILABOD_JSON_KEY)
      return r.json()
  except Exception as e:
    return []

def get_current_school(path_variables):
  try:
    try:
      return path_variables['school_id']
    except:
      return path_variables['pk']
  except:
    return None

def is_school_manager(request, kwargs):
  if request.user.is_superuser:
    return True
  elif not request.user.is_authenticated:
    return False

  try:
    school_id = get_current_school(kwargs)
    if school_id and School.objects.filter(pk=school_id).filter(managers=Manager.objects.filter(user=request.user)):
      return True
  except Exception as e:
    pass
  return False

def is_manager(request):
  if not request.user.is_authenticated:
    return False
  try:
    if Manager.objects.filter(user=request.user):
      return True
  except:
    pass
  return False

def is_school_teacher(request, kwargs):
  if not request.user.is_authenticated:
    return False
  try:
    school_id = get_current_school(kwargs)
    if school_id and School.objects.filter(pk=school_id).filter(teachers=Teacher.objects.filter(user=request.user)):
      return True
  except:
    pass
  return False

def is_teacher(request):
  if not request.user.is_authenticated:
    return False
  try:
    if Teacher.objects.filter(user=request.user):
      return True
  except:
    pass
  return False


def is_group_manager(request, kwargs):
  if not request.user.is_authenticated:
    return False
  try:
    try:
      if StudentGroup.objects.filter(pk=kwargs['student_group']).filter(group_managers=Teacher.objects.filter(user=request.user)):# user=context.request.user)):
        return True
    except:
      if 'survey_id' in kwargs:
        survey_id = kwargs['survey_id']
      else:
        survey_id = kwargs['pk']
      if StudentGroup.objects.filter(pk=Survey.objects.get(pk=survey_id).studentgroup.id).filter(group_managers=Teacher.objects.filter(user=request.user)):# user=context.request.user)):
        return True
  except:
    pass
  return False

def slug_sort(q, attr):
  return sorted(q, key=lambda x: slugify(getattr(x,attr)))

def calc_survey_results(survey_identifier, click_values, input_values):
  if survey_identifier:
    if 'b_LF_' in survey_identifier:
      try:
        words_read = int(click_values[-1].split(',')[0]) - len(click_values)
        time_read = 120
        try:
          time_read = int(input_values.get('b1_LF_timi', 120))
        except:
          return ""
        return str(int(words_read / time_read * 60)) + " orð/mín"
      except:
        return ""
    else:
      return ""
  return click_values
