# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db                  import models
from django                     import forms
from django.contrib.auth.models import User
from django.utils               import timezone

import json


class Notification(models.Model):
    notification_type = models.CharField(max_length = 128)
    notification_id   = models.IntegerField()
    user              = models.ForeignKey(User)

    class Meta:
        unique_together = (("notification_type", "notification_id"),)


class Manager(models.Model):
    ssn      = models.CharField(max_length = 10, unique=True)
    name     = models.CharField(max_length = 128)
    email    = models.CharField(max_length = 256, blank=True)
    phone    = models.CharField(max_length = 7, blank=True)
    position = models.CharField(max_length = 256, blank=True)
    user     = models.ForeignKey(User)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class ManagerForm(forms.ModelForm):
    class Meta:
        model   = Manager
        fields  = ['ssn', 'name', 'email', 'phone', 'position', 'user']
        widgets = {'user': forms.HiddenInput()}
        labels  = {
            'ssn'     : 'Kennitala',
            'name'    : 'Nafn',
            'email'   : 'Tölvupóstfang',
            'phone'   : 'Símanúmer',
            'position': 'Staða',
            'user'    : 'Notendur',
        }


class Teacher(models.Model):
    ssn      = models.CharField(max_length = 10, unique=True)
    name     = models.CharField(max_length = 128)
    position = models.CharField(max_length = 256, blank=True)
    user     = models.ForeignKey(User)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class TeacherForm(forms.ModelForm):
    class Meta:
        model   = Teacher
        fields  =  ['ssn', 'name', 'position', 'user']
        widgets = {'user': forms.HiddenInput()}
        labels  = {
            'ssn'     : 'Kennitala',
            'name'    : 'Nafn',
            'position': 'Staða',
            'user'    : 'Notendur',
        }


class Student(models.Model):
    ssn  = models.CharField(max_length = 10, unique=True)
    name = models.CharField(max_length = 128)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class StudentForm(forms.ModelForm):
    class Meta:
        model  = Student
        fields =  ['ssn', 'name']
        labels = {
            'ssn' : 'Kennitala',
            'name': 'Nafn',
        }


class School(models.Model):
    name     = models.CharField(max_length = 128)
    ssn      = models.CharField(max_length = 10)
    managers = models.ManyToManyField(Manager, blank=True)
    teachers = models.ManyToManyField(Teacher, blank=True)
    students = models.ManyToManyField(Student, blank=True)

    def __str__(self):
        return self.name + " (" + self.ssn + ")"

    class Meta:
        ordering = ["name"]


class SchoolForm(forms.ModelForm):
    class Meta:
        model   = School
        fields  = '__all__'
        widgets = {'group': forms.HiddenInput()}
        labels  = {
            'name'    : 'Nafn',
            'ssn'     : 'Kennitala',
            'managers': 'Stjórnendur',
            'teachers': 'Kennarar',
            'students': 'Nemendur',
        }


class StudentGroup(models.Model):
    name  = models.CharField(max_length = 128)
    YEARS = (
        ('0', 'Blandaður árgangur'),
        ('1', '1. bekkur'),
        ('2', '2. bekkur'),
        ('3', '3. bekkur'),
        ('4', '4. bekkur'),
        ('5', '5. bekkur'),
        ('6', '6. bekkur'),
        ('7', '7. bekkur'),
        ('8', '8. bekkur'),
        ('9', '9. bekkur'),
        ('10', '10. bekkur'),
    )
    student_year   = models.CharField(max_length = 2, choices=YEARS, null=True, blank=True)
    group_managers = models.ManyToManyField(Teacher, blank=True)
    school         = models.ForeignKey('School')
    students       = models.ManyToManyField(Student, blank=True)

    def __str__(self):
        return self.name


class StudentGroupForm(forms.ModelForm):
    class Meta:
        model   = StudentGroup
        fields  = ['name', 'student_year',
                   'group_managers', 'school', 'students']
        widgets = {'school': forms.HiddenInput()}
        labels  = {
            'name'          : 'Nafn',
            'student_year'  : 'Árgangur',
            'group_managers': 'Kennarar',
            'school'        : 'Skóli',
            'students'      : 'Nemendur',
        }


class Survey(models.Model):
    studentgroup = models.ForeignKey('StudentGroup')
    survey       = models.CharField(max_length = 1024)            # survey id from profagrunnur
    title        = models.CharField(max_length = 256)             # value from profagrunnur
    identifier   = models.CharField(max_length = 256, null=True)  # value from profagrunnur
    active_from  = models.DateField(default=timezone.now)         # value from profagrunnur
    active_to    = models.DateField(default=timezone.now)         # value from profagrunnur

    def is_expired(self):
        if timezone.now().date() > self.active_to:
            return True
        return False

    def results(self):
        return SurveyResult.objects.filter(survey=self)

    def __str__(self):
        return self.title + " (" + self.survey + ")"


class SurveyForm(forms.ModelForm):
    class Meta:
        model   = Survey
        fields  = ['studentgroup', 'survey', 'title', 'identifier', 'active_from', 'active_to']
        widgets = {
            'studentgroup': forms.HiddenInput(),
            'survey'      : forms.HiddenInput(),
            'identifier'  : forms.HiddenInput(),
            'title'       : forms.HiddenInput(),
            'active_from' : forms.HiddenInput(),
            'active_to'   : forms.HiddenInput(),
        }
        labels = {
            'studentgroup': 'Nemendahópur',
            'survey'      : 'Könnun',
            'identifier'  : 'Auðkenniskóði',
            'title'       : 'Titill',
            'active_from' : 'Virkt frá',
            'active_to'   : 'Virkt til',
        }


class SurveyResult(models.Model):
    student     = models.ForeignKey('Student')
    created_at  = models.DateTimeField(default=timezone.now)
    results     = models.TextField()
    reported_by = models.ForeignKey('Teacher')
    survey      = models.ForeignKey('Survey')  # url to survey
    created_at  = models.DateField(default=timezone.now)

    @classmethod
    def get_results(cls, id):
        return json.loads(cls(pk=id).results)


class SurveyResultForm(forms.ModelForm):
    class Meta:
        model  = SurveyResult
        fields = []
        labels = {
            'student'    : 'Nemandi',
            'created_at' : 'Búið til',
            'results'    : 'Niðurstöður',
            'reported_by': 'Skýrsla frá',
            'survey'     : 'Könnun',
        }


class SurveyLogin(models.Model):
    student     = models.ForeignKey(Student)
    survey_id   = models.CharField(max_length = 256)  # external survey identity
    survey_code = models.CharField(max_length = 16)


class SurveyLoginForm(forms.ModelForm):
    file = forms.FileField()

    class Meta:
        model  = SurveyLogin
        fields = ['student', 'survey_id', 'survey_code']
        labels = {
            'student'    : 'Nemandi',
            'survey_id'  : 'Könnunarnúmer',
            'survey_code': 'Könnunarkóði',
        }


class SuperUserForm(forms.ModelForm):
    class Meta:
        model  = User
        fields = ['username', 'is_superuser']
        labels = {
            'username'    : 'Kennitala',
            'is_superuser': 'Umsjónarmaður',
        }
