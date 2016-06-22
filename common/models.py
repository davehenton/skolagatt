# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.models import Group
from django.utils import timezone

from datetime import datetime
import json

class Manager(models.Model):
	ssn = models.CharField(max_length = 10, unique=True)
	name = models.CharField(max_length = 128)
	user = models.ForeignKey(User)

	class Meta:
		ordering = ["-name"]

	def __str__(self):
		return self.name

class ManagerForm(forms.ModelForm):
	class Meta:
		model = Manager
		fields = ['ssn', 'name', 'user']
		widgets = {'user': forms.HiddenInput()}

class Teacher(models.Model):
	ssn = models.CharField(max_length = 10, unique=True)
	name = models.CharField(max_length = 128)
	user = models.ForeignKey(User)

	class Meta:
		ordering = ["-name"]

	def __str__(self):
		return self.name

class TeacherForm(forms.ModelForm):
	class Meta:
		model = Teacher
		fields =  ['ssn', 'name', 'user']
		widgets = {'user': forms.HiddenInput()}

class Student(models.Model):
	ssn = models.CharField(max_length = 10, unique=True)
	name = models.CharField(max_length = 128)

	class Meta:
		ordering = ["name"]

	def __str__(self):
		return self.name

class StudentForm(forms.ModelForm):
	class Meta:
		model = Student
		fields =  ['ssn', 'name']

class School(models.Model):
	name = models.CharField(max_length = 128)
	ssn = models.CharField(max_length = 10)
	managers = models.ManyToManyField(Manager, blank=True)
	teachers = models.ManyToManyField(Teacher, blank=True)
	students = models.ManyToManyField(Student, blank=True)

	def __str__(self):
		return self.name + " (" + self.ssn + ")"

	class Meta:
		ordering = ["name"]

class SchoolForm(forms.ModelForm):
	class Meta:
		model = School
		fields = '__all__'
		widgets = {'group': forms.HiddenInput()}

class StudentGroup(models.Model):
	name = models.CharField(max_length = 128)
	student_year = models.CharField(max_length = 2, null=True, blank=True)
	group_managers = models.ManyToManyField(Teacher, blank=True)
	school = models.ForeignKey('School')
	students = models.ManyToManyField(Student, blank=True)

	def __str__(self):
		return self.name

class StudentGroupForm(forms.ModelForm):
	class Meta:
		model = StudentGroup
		fields =  ['name', 'student_year', 'group_managers', 'school', 'students']
		widgets = {'school': forms.HiddenInput()}

class Survey(models.Model):
	studentgroup = models.ForeignKey('StudentGroup')
	survey = models.CharField(max_length = 1024) #survey id from profagrunnur
	title = models.CharField(max_length = 256) #value from profagrunnur
	active_from = models.DateField(default=timezone.now) #value from profagrunnur
	active_to = models.DateField(default=timezone.now) #value from profagrunnur

	def results(self):
		return SurveyResult.objects.filter(survey=self)

class SurveyForm(forms.ModelForm):
	class Meta:
		model = Survey
		fields =  ['studentgroup', 'survey', 'title', 'active_from', 'active_to']
		widgets= {
			'studentgroup': forms.HiddenInput(),
			'survey': forms.HiddenInput(),
			'title': forms.HiddenInput(),
			'active_from': forms.HiddenInput(),
			'active_to': forms.HiddenInput(),
		}

class SurveyResult(models.Model):
	student = models.ForeignKey('Student')
	created_at = models.DateTimeField(default=timezone.now)
	results = models.TextField()
	reported_by = models.ForeignKey('Teacher')
	survey = models.ForeignKey('Survey') #url to survey

	@classmethod
	def get_results(cls, id):
		return json.loads(cls(pk=id).results)

class SurveyResultForm(forms.ModelForm):
	class Meta:
		model = SurveyResult
		fields = []

class SurveyLogin(models.Model):
	student = models.ForeignKey(Student)
	survey_id = models.CharField(max_length = 256) #external survey identity
	survey_code = models.CharField(max_length = 16)

class SurveyLoginForm(forms.ModelForm):
	file = forms.FileField()
	class Meta:
		model = SurveyLogin
		fields = ['student', 'survey_id', 'survey_code']