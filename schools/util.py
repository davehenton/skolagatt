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


def get_aldursbil(kennitala):
    '''Takes kennitala, returns aldursbil (age level)'''
    # INPUT: kennitala/ssn. preferably a string like DDMMYYXXXX
    # where DD is date, MM month, YY year, rest we don't care about.
    # OUTPUT: aldursbil. "bil 1", "bil 2", "bil 3"
    # where bil 1 means was born in jan-may, 2 means apr-aug, 3 means sep-dec.
    month = int(kennitala[2:4])
    third_of_year = int(max(0, month - 1)/ 4)  # rounds down
    third_to_aldursbil = {0: 'bil 1', 1: 'bil 2', 2: 'bil 3'}
    return third_to_aldursbil[third_of_year]


def lesskilnings_hopar_1(hljodkerfisvitund_sum, malthroski_sum, bokstafathekking_sum):
  '''
  Lesskilnings hópar fyrir börn fædd á fyrsta ársþriðjungi
  '''
  hopar = []
  if hljodkerfisvitund_sum == -1:
    hopar.append('Vantar gögn')
  elif hljodkerfisvitund_sum <= 18:
    hopar.append('Áhætta 1 (%d)'%(hljodkerfisvitund_sum))
  elif hljodkerfisvitund_sum <= 21:
    hopar.append('Áhætta 2 (%d)'%(hljodkerfisvitund_sum))
  elif hljodkerfisvitund_sum <= 23:
    hopar.append('Óvissa (%d)'%(hljodkerfisvitund_sum))
  else:
    hopar.append('Utan áhættu')

  if malthroski_sum == -1:
    hopar.append('Vantar gögn')
  elif malthroski_sum <= 17:
    hopar.append('Áhætta 1 (%d)'%(malthroski_sum))
  elif malthroski_sum <= 18:
    hopar.append('Áhætta 2 (%d)'%(malthroski_sum))
  elif malthroski_sum <= 19:
    hopar.append('Óvissa (%d)'%(malthroski_sum))
  else:
    hopar.append('Utan áhættu')

  if bokstafathekking_sum == -1:
    hopar.append('Vantar gögn')
  elif bokstafathekking_sum <= 11:
    hopar.append('Áhætta 1 (%d)'%(bokstafathekking_sum))
  elif bokstafathekking_sum <= 14:
    hopar.append('Áhætta 2 (%d)'%(bokstafathekking_sum))
  elif bokstafathekking_sum <= 15:
    hopar.append('Óvissa (%d)'%(bokstafathekking_sum))
  else:
    hopar.append('Utan áhættu')

  return hopar


def lesskilnings_hopar_2(hljodkerfisvitund_sum, malthroski_sum, bokstafathekking_sum):
  '''
  Lesskilnings hópar fyrir börn fædd á öðrum ársþriðjungi
  '''
  hopar = []
  if hljodkerfisvitund_sum == -1:
    hopar.append('Vantar gögn')
  elif hljodkerfisvitund_sum <= 15:
    hopar.append('Áhætta 1 (%d)'%(hljodkerfisvitund_sum))
  elif hljodkerfisvitund_sum <= 18:
    hopar.append('Áhætta 2 (%d)'%(hljodkerfisvitund_sum))
  elif hljodkerfisvitund_sum <= 20:
    hopar.append('Óvissa')
  else:
    hopar.append('Utan áhættu')

  if malthroski_sum == -1:
    hopar.append('Vantar gögn')
  elif malthroski_sum <= 14:
    hopar.append('Áhætta 1 (%d)'%(malthroski_sum))
  elif malthroski_sum <= 17:
    hopar.append('Áhætta 2 (%d)'%(malthroski_sum))
  elif malthroski_sum <= 18:
    hopar.append('Óvissa (%d)'%(malthroski_sum))
  else:
    hopar.append('Utan áhættu')

  if bokstafathekking_sum == -1:
    hopar.append('Vantar gögn')
  elif bokstafathekking_sum <= 10:
    hopar.append('Áhætta 1 (%d)'%(bokstafathekking_sum))
  elif bokstafathekking_sum <= 13:
    hopar.append('Áhætta 2 (%d)'%(bokstafathekking_sum))
  elif bokstafathekking_sum <= 14:
    hopar.append('Óvissa (%d)'%(bokstafathekking_sum))
  else:
    hopar.append('Utan áhættu')

  return hopar


def lesskilnings_hopar_3(hljodkerfisvitund_sum, malthroski_sum, bokstafathekking_sum):
  '''
  Lesskilnings hópar fyrir börn fædd á þriðja ársþriðjungi
  '''
  hopar = []
  if hljodkerfisvitund_sum == -1:
    hopar.append('Vantar gögn')
  elif hljodkerfisvitund_sum <= 16:
    hopar.append('Áhætta 1 (%d)'%(hljodkerfisvitund_sum))
  elif hljodkerfisvitund_sum <= 19:
    hopar.append('Áhætta 2 (%d)'%(hljodkerfisvitund_sum))
  elif hljodkerfisvitund_sum <= 20:
    hopar.append('Óvissa (%d)'%(hljodkerfisvitund_sum))
  else:
    hopar.append('Utan áhættu')

  if malthroski_sum == -1:
    hopar.append('Vantar gögn')
  elif malthroski_sum <= 14:
    hopar.append('Áhætta 1 (%d)'%(malthroski_sum))
  elif malthroski_sum <= 16:
    hopar.append('Áhætta 2 (%d)'%(malthroski_sum))
  elif malthroski_sum <= 17:
    hopar.append('Óvissa (%d)'%(malthroski_sum))
  else:
    hopar.append('Utan áhættu')

  if bokstafathekking_sum == -1:
    hopar.append('Vantar gögn')
  elif bokstafathekking_sum <= 9:
    hopar.append('Áhætta 1 (%d)'%(bokstafathekking_sum))
  elif bokstafathekking_sum <= 11:
    hopar.append('Áhætta 2 (%d)'%(bokstafathekking_sum))
  elif bokstafathekking_sum <= 13:
    hopar.append('Óvissa (%d)'%(bokstafathekking_sum))
  else:
    hopar.append('Utan áhættu')

  return hopar


def lesskilnings_hopar(aldursbil, input_values):
  '''
  Finna lesskilnings hópa eftir aldursbili úr niðurstöðum prófa
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

  # hljodkerfisvitund_sum = sum([ int(value) for key, value in input_values.items() if key.startswith("hljod_") and value.isdigit() ])
  # Same thing for keys that start with 'mal_'
  # malthroski_sum = sum([ int(value) for key, value in input_values.items() if key.startswith("mal_") and value.isdigit() ])
  # And again for keys that start with 'bok_'
  # bokstafathekking_sum = sum([ int(value) for key, value in input_values.items() if key.startswith("bok_") and value.isdigit() ])

  if aldursbil == 'bil 1':
    return lesskilnings_hopar_1(lesskilnings_sums["hljod_"], lesskilnings_sums["mal_"], lesskilnings_sums["bok_"])
  elif aldursbil == 'bil 2':
    return lesskilnings_hopar_1(lesskilnings_sums["hljod_"], lesskilnings_sums["mal_"], lesskilnings_sums["bok_"])
  else:
    return lesskilnings_hopar_1(lesskilnings_sums["hljod_"], lesskilnings_sums["mal_"], lesskilnings_sums["bok_"])


def calc_survey_results(survey_identifier, click_values, input_values, student):
  if survey_identifier:
    if survey_identifier.startswith('01b_LTL_'):
        try:
          aldursbil = get_aldursbil(student.ssn)
          return lesskilnings_hopar(aldursbil, input_values)
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
        return list(str(int(words_read / time_read * 60)) + " orð/mín")
      except:
        return [""]
    else:
      return [""]
  return click_values
