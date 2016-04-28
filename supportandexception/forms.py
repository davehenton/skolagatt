# -*- coding: utf-8 -*-
from django.db import models
from django import forms
from django.forms import *
from .models import *

#from django.forms import *

from common.models import *



#class StudentsForm(forms.ModelForm):
#	class Meta:
#		model = 'student'
#		fields = ['socialsecurity','name']
#		labels = {
#			'socialsecurity': 'Kennitala',
#			'name': 'Nafn',
#		}

class UploadFileForm(forms.Form):
    file = forms.FileField()


support_title = (
	('reading_assistance','Lestraraðstoð'),
	('interpretation','Túlkun fyrirmæla'),
	('return_to_sites','Fái að að skila ritun á vefsvæði'),
	('longer_time','Lengdur próftími'),
)

reading_assistance = (
	(1,'Íslenska'),
	(2,'Enska'),
	(3,'Stærðfræði'),
	)
interpretation = (
	(1,'Íslenska'),
	(2,'Enska'),
	(3,'Stærðfræði'),
	)
return_to_sites = (
	(1,'Íslenska'),
	(2,'Enska'),
	(3,'Stærðfræði'),
	)
longer_time = (
	(1,'Íslenska'),
	(2,'Enska'),
	(3,'Stærðfræði'),
	)
class SupportResourceForm(forms.ModelForm):
	support_title = forms.ChoiceField(required = False, widget = forms.CheckboxSelectMultiple, choices = support_title)
	reading_assistance = forms.ChoiceField(required = False, widget = forms.CheckboxSelectMultiple, choices = reading_assistance)
	interpretation = forms.ChoiceField(required = False, widget = forms.CheckboxSelectMultiple, choices = interpretation)
	return_to_sites = forms.ChoiceField(required = False, widget = forms.CheckboxSelectMultiple, choices = return_to_sites)
	longer_time = forms.ChoiceField(required = False, widget = forms.CheckboxSelectMultiple, choices = longer_time)
	
	class Meta:
		model = SupportResource
		fields = '__all__'

exam_choices = (
	(1,'Íslenska'),
	(2,'Enska'),
	(3,'Stærðfræði'),
	)
reason_choices = (
	(1, 'Nemendur með annað móðurmál en íslensku sem geta fengið undanþágu frá því að þreyta samræmt könnunarpróf í íslensku í 4., 7. og 10. bekk. Jafnframt er heimilt að veita þessum nemendum undanþágu frá því að þreyta samræmt könnunarpróf í stærðfræði hafi þeir dvalið skemur á landinu en eitt ár. Sama á við um nemendur sem ekki hafa lært ensku'),
 	(2, 'Nemendur í sérskólum, sérdeildum og aðra þá nemendur á skyldunámsaldri sem taldir eru víkja svo frá almennum þroska að þeim henti ekki samræmt könnunarpróf.'),
 	(3, 'Nemendur sem orðið hafa fyrir líkamlegu eða andlegu áfalli sem gerir þeim ókleift að þreyta samræmt könnunarpróf'),
 )

class ExceptionsForm(forms.ModelForm):
	exam = forms.ChoiceField(required = False, widget = forms.CheckboxSelectMultiple(attrs= {'inline': True,},), choices = exam_choices)
	reason = forms.ChoiceField(required = False, widget = forms.RadioSelect, choices = reason_choices)
	class Meta:
		model = Exceptions
		fields = '__all__'

SupportResourceFormSet = formset_factory(SupportResourceForm)