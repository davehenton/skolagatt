# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.models import Group
from django.utils import timezone

from datetime import datetime
import json

class Notification(models.Model):
	notification_type = models.CharField(max_length = 128)
	notification_id = models.IntegerField()
	user = models.ForeignKey(User)

	class Meta:
		unique_together = (("notification_type", "notification_id"),)


class Manager(models.Model):
	ssn = models.CharField(max_length = 10, unique=True)
	name = models.CharField(max_length = 128)
	email = models.CharField(max_length = 256, blank=True)
	phone = models.CharField(max_length = 7, blank=True)
	position = models.CharField(max_length = 256, blank=True)
	user = models.ForeignKey(User)

	class Meta:
		ordering = ["name"]

	def __str__(self):
		return self.name


class Teacher(models.Model):
	ssn = models.CharField(max_length = 10, unique=True)
	name = models.CharField(max_length = 128)
	position = models.CharField(max_length = 256, blank=True)	
	user = models.ForeignKey(User)

	class Meta:
		ordering = ["name"]

	def __str__(self):
		return self.name


class Student(models.Model):
	ssn = models.CharField(max_length = 10, unique=True)
	name = models.CharField(max_length = 128)

	class Meta:
		ordering = ["name"]

	def __str__(self):
		return self.name



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



class StudentGroup(models.Model):
	name = models.CharField(max_length = 128)
	YEARS = (
		('0','Blandaður árgangur'),
		('1','1. bekkur'),
		('2','2. bekkur'),
		('3','3. bekkur'),
		('4','4. bekkur'),
		('5','5. bekkur'),
		('6','6. bekkur'),
		('7','7. bekkur'),
		('8','8. bekkur'),
		('9','9. bekkur'),
		('10','10. bekkur'),
	)
	student_year = models.CharField(max_length = 2, choices=YEARS, null=True, blank=True)	
	group_managers = models.ManyToManyField(Teacher, blank=True)
	school = models.ForeignKey('School')
	students = models.ManyToManyField(Student, blank=True)

	def __str__(self):
		return self.name

class Survey(models.Model):
	studentgroup = models.ForeignKey('StudentGroup')
	survey = models.CharField(max_length = 1024) #survey id from profagrunnur
	title = models.CharField(max_length = 256) #value from profagrunnur
	identifier = models.CharField(max_length = 256,null=True) #value from profagrunnur
	active_from = models.DateField(default=timezone.now) #value from profagrunnur
	active_to = models.DateField(default=timezone.now) #value from profagrunnur

	def is_expired(self):
		if timezone.now().date() > self.active_to:
			return True
		return False

	def results(self):
		return SurveyResult.objects.filter(survey=self)

	def __str__(self):
		return self.title + " (" + self.survey + ")"



class SurveyResult(models.Model):
	student = models.ForeignKey('Student')
	created_at = models.DateTimeField(default=timezone.now)
	results = models.TextField()
	reported_by = models.ForeignKey('Teacher')
	survey = models.ForeignKey('Survey') #url to survey
	created_at = models.DateField(default=timezone.now)

	@classmethod
	def get_results(cls, id):
		return json.loads(cls(pk=id).results)

class SurveyLogin(models.Model):
	student = models.ForeignKey(Student)
	survey_id = models.CharField(max_length = 256) #external survey identity
	survey_code = models.CharField(max_length = 16)

