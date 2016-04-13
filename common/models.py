# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django import forms
from django.contrib.auth.models import User

class UserMethods(User):
	def get_schools(self):
		schools = Manager.objects.filter(ssn=self.username)
		schools.append(Teacher.objects.filter(ssn=self.username))
		return schools
	class Meta:
		proxy=True

class School(models.Model):
	name = models.CharField(max_length = 128)
	ssn = models.CharField(max_length = 10)

	def __str__(self):
		return self.name + " (" + self.ssn + ")"

class SchoolForm(forms.ModelForm):
	class Meta:
		model = School
		fields = '__all__'

class Manager(models.Model):
	ssn = models.CharField(max_length = 10)
	name = models.CharField(max_length = 128)
	schools = models.ManyToManyField(School)
	# many to many school = models.ForeignKey('School')

	class Meta:
		ordering = ["-name"]

	def __str__(self):
		return self.name

class ManagerForm(forms.ModelForm):
	class Meta:
		model = Manager
		fields = '__all__'

class Teacher(models.Model):
	ssn = models.CharField(max_length = 10)
	name = models.CharField(max_length = 128)
	schools = models.ManyToManyField(School)
	# many to many school = models.ForeignKey('School')

	class Meta:
		ordering = ["-name"]

	def __str__(self):
		return self.name

class TeacherForm(forms.ModelForm):
	class Meta:
		model = Teacher
		fields = '__all__'

class StudentGroup(models.Model):
	name = models.CharField(max_length = 128)
	student_year = models.CharField(max_length = 2, null=True, blank=True)
	group_managers = models.ManyToManyField(Teacher)
	school = models.ForeignKey('School')

	def __str__(self):
		return self.name

class StudentGroupForm(forms.ModelForm):
	class Meta:
		model = StudentGroup
		fields = '__all__'

class Student(models.Model):
	ssn = models.CharField(max_length = 10)
	name = models.CharField(max_length = 128)
	# many to many school = models.ForeignKey('School')
	schools = models.ManyToManyField(School)
	student_groups = models.ManyToManyField(StudentGroup, blank=True)

	class Meta:
		ordering = ["-name"]

	def __str__(self):
		return self.name

class StudentForm(forms.ModelForm):
	class Meta:
		model = Student
		fields = '__all__'
