<<<<<<< HEAD
def aldursbil(kennitala):
    '''Takes kennitala, returns aldursbil (age level)'''
    # INPUT: kennitala/ssn. preferably a string like DDMMYYXXXX
    # where DD is date, MM month, YY year, rest we don't care about.
    # OUTPUT: aldursbil. "bil 1", "bil 2", "bil 3"
    # where bil 1 means was born in jan-may, 2 means apr-aug, 3 means sep-dec.
    if not is_kennitala_valid(kennitala):
        # we have an error
        return "villa"
    else:
        month = int(kennitala[2:4])
        third_of_year = int(max(0, month - 1) / 4)  # rounds down
        third_to_aldursbil = {0: 'bil 1', 1: 'bil 2', 2: 'bil 3'}
        return third_to_aldursbil[third_of_year]


def is_kennitala_valid(kennitala):
    '''Returns false if kennitala/ssn is unusable to get date of birth'''
    # Temporary function. We're gonna write something more elegant connecting
    # to Thjodskra's kennitalas
    if not kennitala.isdigit():
        return False
    else:
        if len(str(kennitala)) < 6:
            return False
        elif not kennitala[0:2].isdigit() or not kennitala[2:4].isdigit() or not kennitala[4:6].isdigit():
            return False
        elif 1 > int(kennitala[0:2]) or 31 < int(kennitala[0:2]) or 1 > int(kennitala[2:4]) or 12 < int(kennitala[2:4]):
            # could've imported dateutils.parser to check (but we're gonna use thjodskra to check)
            return False
        else:
            return True
=======
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

def lesskilnings_results(input_values):
  '''
  Skilum niðurstöðum prófs í lesskilningi
  '''
  # Cycle through input_values, sum up all values where the key starts with 'hljod_', 'mal_', 'bok_'. Checks for input errors.
  lesskilnings_sums = {'hljod_': 0, 'mal_': 0, 'bok_': 0}
  for key, value in input_values.items():
    for type_sum in lesskilnings_sums.keys():
      # type = 'hljod_' for instance, type_sum for 'hljod_' starts as 0
      if key.startswith(type_sum):
        if not str(value).isdigit():
          # Input error so we will make this type_sum permanently = -1 to indicate error
          lesskilnings_sums[type_sum] = -1
        elif str(value).isdigit() and not lesskilnings_sums[type_sum] == -1:
          # Not input error so let's add up
          lesskilnings_sums[type_sum] += int(value)

  hopar = []
  if lesskilnings_sums["hljod_"] == -1:
    hopar.append('Vantar gögn')
  elif lesskilnings_sums["hljod_"] <= 14:
    hopar.append('Áhætta 1')
  elif lesskilnings_sums["hljod_"] <= 17:
    hopar.append('Áhætta 2')
  elif lesskilnings_sums["hljod_"] <= 19:
    hopar.append('Óvissa')
  else:
    hopar.append('Utan áhættu')

  if lesskilnings_sums["mal_"] == -1:
    hopar.append('Vantar gögn')
  elif lesskilnings_sums["mal_"] <= 14:
    hopar.append('Áhætta 1')
  elif lesskilnings_sums["mal_"] <= 16:
    hopar.append('Áhætta 2')
  elif lesskilnings_sums["mal_"] <= 17:
    hopar.append('Óvissa')
  else:
    hopar.append('Utan áhættu')

  if lesskilnings_sums["bok_"] == -1:
    hopar.append('Vantar gögn')
  elif lesskilnings_sums["bok_"] <= 7:
    hopar.append('Áhætta 1')
  elif lesskilnings_sums["bok_"] <= 10:
    hopar.append('Áhætta 2')
  elif lesskilnings_sums["bok_"] <= 12:
    hopar.append('Óvissa')
  else:
    hopar.append('Utan áhættu')

  return hopar

def calc_survey_results(survey_identifier, click_values, input_values, student):
  if survey_identifier:
    if survey_identifier.startswith('01b_LTL_'):
        try:
          return lesskilnings_results(input_values)
        except Exception as e:
          return ["error"]
    elif '_LF_' in survey_identifier:
      try:
        words_read = int(click_values[-1].split(',')[0]) - len(click_values)
        time_read = 120
        try:
          time_read = int(input_values.get('b1_LF_timi', 120))
        except:
          return [""]
        return [str(int(words_read / time_read * 60)) + " orð/mín"]
      except:
        return [""]
    else:
      return [""]
  return click_values
>>>>>>> 53f0f8b0031a2f1b69dc6537d7ac96652cc4cbec
