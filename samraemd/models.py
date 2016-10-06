# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django import forms

from common.models import *

# Create your models here.

class SamraemdMathResult(models.Model):
	student = models.ForeignKey(Student)
	#data fields
	#Samræmd einkunn
	ra_se = models.CharField(max_length = 4)
	rm_se = models.CharField(max_length = 4)
	tt_se = models.CharField(max_length = 4)
	se = models.CharField(max_length = 4)
	#Raðeinkunn
	ra_re = models.IntegerField()
	rm_re = models.IntegerField()
	tt_re = models.IntegerField()
	re = models.IntegerField()
	#Grunnskólaeinkunn
	ra_sg = models.IntegerField()
	rm_sg = models.IntegerField()
	tt_sg = models.IntegerField()
	sg = models.IntegerField()
	ord_talna_txt = models.CharField(max_length = 128)
	#Framfaraeinkunn	
	fm_fl = models.IntegerField(blank=True)
	fm_txt = models.CharField(max_length = 256, blank=True)
	#exam fields
	exam_code = models.CharField(max_length = 128)
	exam_date = models.DateField()

class SamraemdMathResultForm(forms.ModelForm):
	file = forms.FileField()
	class Meta:
		model = SamraemdMathResult
		fields = ['ra_se', 'rm_se', 'tt_se', 'se', 'ra_re', 'rm_re', 'tt_re', 're', 'ra_sg', 'rm_sg', 'tt_sg', 'sg', 'ord_talna_txt', 'fm_fl', 'fm_txt', 'exam_code', 'exam_date']
		labels = {
			'exam_code': 'Prófkóði',
			'student': 'Nemandi',
			'ra_se': 'Samræmd einkunn - Reikningur og aðgerðir',
			'rm_se': 'Samræmd einkunn - Rúmfræði og mælingar',
			'tt_se': 'Samræmd einkunn - Tölur og talnaskilningur',
			'se': 'Samræmd einkunn - Heild',
			'ra_re': 'Raðeinkunn - Reikningur og aðgerðir',
			'rm_re': 'Raðeinkunn - Rúmfræði og mælingar',
			'tt_re': 'Raðeinkunn - Tölur og talnaskilningur',
			're': 'Raðeinkunn - Heild',
			'ra_sg': 'Grunnskólaeinkunn - Reikningur og aðgerðir',
			'rm_sg': 'Grunnskólaeinkunn - Rúmfræði og mælingar',
			'tt_sg': 'Grunnskólaeinkunn - Tölur og talnaskilningur',
			'sg': 'Grunnskólaeinkunn - Heild',
			'ord_talna_txt': 'Orðadæmi og talnadæmi',
			'fm_fl': 'Framfaraflokkur',
			'fm_txt': 'Framfaratexti',
			'exam_date': 'Dagsetning prófs (YYYY-MM-DD)'
		}

class SamraemdISLResult(models.Model):
	student = models.ForeignKey(Student)
	#data fields
	#Samræmd einkunn
	le_se = models.CharField(max_length=4)
	mn_se = models.CharField(max_length=4)
	ri_se = models.CharField(max_length=4)
	se = models.CharField(max_length=4)
	#Raðeinkunn
	le_re = models.IntegerField()
	mn_re = models.IntegerField()
	ri_re = models.IntegerField()
	re = models.IntegerField()
	#Grunnskólaeinkunn
	le_sg = models.IntegerField()
	mn_sg = models.IntegerField()
	ri_sg = models.IntegerField()
	sg = models.IntegerField()
	#Framfaraeinkunn	
	fm_fl = models.IntegerField(blank=True)
	fm_txt = models.CharField(max_length = 256, blank=True)
	#exam fields
	exam_code = models.CharField(max_length = 256)
	exam_date = models.DateField()

class SamraemdISLResultForm(forms.ModelForm):
	file = forms.FileField()
	class Meta:
		model = SamraemdISLResult
		fields = ['le_se', 'mn_se', 'ri_se', 'se', 'le_re', 'mn_re', 'ri_re', 're', 'le_sg', 'mn_sg', 'ri_sg', 'sg', 'fm_fl', 'fm_txt', 'exam_code', 'exam_date']
		labels = {
			'exam_code': 'Prófkóði',
			'student': 'Nemandi',
			'le_se': 'Samræmd einkunn - Lestur',
			'mn_se': 'Samræmd einkunn - Málnotkun',
			'ri_se': 'Samræmd einkunn - Ritun',
			'se': 'Samræmd einkunn - Heild',
			'le_re': 'Raðeinkunn - Lestur',
			'mn_re': 'Raðeinkunn - Málnotkun',
			'ri_re': 'Raðeinkunn - Ritun',
			're': 'Raðeinkunn - Heild',
			'le_sg': 'Grunnskólaeinkunn - Lestur',
			'mn_sg': 'Grunnskólaeinkunn - Málnotkun',
			'ri_sg': 'Grunnskólaeinkunn - Ritun',
			'sg': 'Grunnskólaeinkunn - Heild',
			'fm_fl': 'Framfaraflokkur',
			'fm_txt': 'Framfaratexti',						
			'exam_date': 'Dagsetning prófs (YYYY-MM-DD)'
		}			