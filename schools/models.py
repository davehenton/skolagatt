# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django import forms
from django.contrib.auth.models import User

class School(models.Model):
  user = models.OneToOneField(User, on_delete=models.CASCADE)
  name = models.CharField(max_length = 128)
  social_security = models.CharField(max_length = 10)

class SchoolForm(forms.ModelForm):
  class Meta:
    model = School
    fields = '__all__'

class StudentClass(models.Model):
  class_name = models.CharField(max_length = 128)
  student_year = models.CharField(max_length = 2)

  def __str__(self):
    return self.class_name

class StudentClassForm(forms.ModelForm):
  class Meta:
    model = StudentClass
    fields = '__all__'

class Student(models.Model):
  social_security = models.CharField(max_length = 10)
  name = models.CharField(max_length = 128)
  school = models.ForeignKey('School')
  student_class = models.ForeignKey('StudentClass', blank=True, null=True)

  class Meta:
    ordering = ["-name"]

  def __str__(self):
    return self.name

class StudentForm(forms.ModelForm):
  class Meta:
    model = Student
    fields = '__all__'

class Teacher(models.Model):
  user = models.OneToOneField(User, on_delete=models.CASCADE)
  #username == social_security
  name = models.CharField(max_length = 128)
  school = models.ForeignKey('School')
  teacher_class = models.ForeignKey('StudentClass', blank=True, null=True)

class TeacherForm(forms.ModelForm):
  class Meta:
    model = Teacher
    fields = '__all__'