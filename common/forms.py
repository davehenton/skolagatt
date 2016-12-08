from django                     import forms
from django.forms.widgets       import SelectDateWidget
from django.utils.translation   import ugettext_lazy as _

from common.models import *		

class ManagerForm(forms.ModelForm):
	class Meta:
		model = Manager
		fields = ['ssn', 'name', 'email', 'phone', 'position', 'user']
		widgets = {'user': forms.HiddenInput()}
		labels = {
			'ssn': 'Kennitala',
			'name': 'Nafn',
			'email': 'Tölvupóstfang',
			'phone': 'Símanúmer',
			'position': 'Staða',
			'user': 'Notendur',
		}


class TeacherForm(forms.ModelForm):
	class Meta:
		model = Teacher
		fields =  ['ssn', 'name', 'position', 'user']
		widgets = {'user': forms.HiddenInput()}
		labels = {
			'ssn': 'Kennitala',
			'name': 'Nafn',
			'position': 'Staða',			
			'user': 'Notendur',
		}

class StudentForm(forms.ModelForm):
	class Meta:
		model = Student
		fields =  ['ssn', 'name']
		labels = {
			'ssn': 'Kennitala',
			'name': 'Nafn',
		}

class SchoolForm(forms.ModelForm):
	class Meta:
		model = School
		fields = '__all__'
		widgets = {'group': forms.HiddenInput()}
		labels = {
			'name': 'Nafn',
			'ssn': 'Kennitala',
			'managers': 'Stjórnendur',
			'teachers': 'Kennarar',
			'students': 'Nemendur',
		}


class StudentGroupForm(forms.ModelForm):
	class Meta:
		model = StudentGroup
		fields =  ['name', 'student_year', 'group_managers', 'school', 'students']
		widgets = {'school': forms.HiddenInput()}
		labels = {
			'name': 'Nafn',
			'student_year': 'Árgangur',
			'group_managers': 'Kennarar',
			'school': 'Skóli',
			'students': 'Nemendur',
		}

class SurveyForm(forms.ModelForm):
	class Meta:
		model = Survey
		fields =  ['studentgroup', 'survey', 'title', 'identifier','active_from', 'active_to']
		widgets= {
			'studentgroup': forms.HiddenInput(),
			'survey': forms.HiddenInput(),
			'identifier': forms.HiddenInput(),
			'title': forms.HiddenInput(),
			'active_from': forms.HiddenInput(),
			'active_to': forms.HiddenInput(),
		}
		labels = {
			'studentgroup': 'Nemendahópur',
			'survey': 'Könnun',
			'identifier': 'Auðkenniskóði',
			'title': 'Titill',
			'active_from': 'Virkt frá',
			'active_to': 'Virkt til',
		}

class SurveyResultForm(forms.ModelForm):
	class Meta:
		model = SurveyResult
		fields = []
		labels = {
			'student': 'Nemandi',
			'created_at': 'Búið til',
			'results': 'Niðurstöður',
			'reported_by': 'Skýrsla frá',
			'survey': 'Könnun',
		}

class SurveyLoginForm(forms.ModelForm):
	file = forms.FileField()
	class Meta:
		model = SurveyLogin
		fields = ['student', 'survey_id', 'survey_code']
		labels = {
			'student': 'Nemandi',
			'survey_id': 'Könnunarnúmer',
			'survey_code': 'Könnunarkóði',
		}

class SuperUserForm(forms.ModelForm):
	class Meta:
		model = User
		fields = ['username', 'is_superuser']
		labels = {
			'username': 'Kennitala',
			'is_superuser': 'Umsjónarmaður',
		}		
