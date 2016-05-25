from common.models import *
from django.utils.text import slugify

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

def is_group_manager(request, kwargs):
  if not request.user.is_authenticated:
    return False
  try:
    if StudentGroup.objects.filter(pk=kwargs['student_group']).filter(group_managers=Teacher.objects.filter(user=request.user)):# user=context.request.user)):
      return True
  except:
    pass
  return False

def slug_sort(q, attr):
  return sorted(q, key=lambda x: slugify(getattr(x,attr)))