# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.models import Group
from django.utils import timezone

from datetime import datetime

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
		ordering = ["-name"]

	def __str__(self):
		return self.name

class StudentForm(forms.ModelForm):
	class Meta:
		model = Student
		fields =  ['ssn', 'name']

class School(models.Model):
	name = models.CharField(max_length = 128)
	ssn = models.CharField(max_length = 10)
	managers = models.ManyToManyField(Manager)
	teachers = models.ManyToManyField(Teacher)
	students = models.ManyToManyField(Student)

	def __str__(self):
		return self.name + " (" + self.ssn + ")"

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
	survey = models.CharField(max_length = 1024) #url to profagrunnur
	title = models.CharField(max_length = 256) #value from profagrunnur
	active_from = models.DateField(default=timezone.now) #value from profagrunnur
	active_to = models.DateField(default=timezone.now) #value from profagrunnur

class SurveyForm(forms.ModelForm):
	class Meta:
		model = Survey
		fields =  ['studentgroup', 'survey', 'title', 'active_from', 'active_to']
		widgets = {
			'survey': forms.TextInput(attrs={'readonly': True}),
			'title': forms.TextInput(attrs={'readonly': True}),
			'active_from': forms.TextInput(attrs={'readonly': True}),
			'active_to': forms.TextInput(attrs={'readonly': True}),
		}

class SurveyResult(models.Model):
	student = models.ForeignKey('Student')
	created_at = models.DateTimeField(default=timezone.now)
	completed_at = models.DateTimeField(default=timezone.now)
	results = models.TextField()
	reported_by = models.ForeignKey('Teacher')
	survey = models.CharField(max_length = 1024) #url to survey