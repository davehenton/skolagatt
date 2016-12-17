# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db                  import models

from django.contrib.auth.models import User
from django.utils               import timezone

import json

from survey.models import Survey


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


class Teacher(models.Model):
    ssn      = models.CharField(max_length = 10, unique=True)
    name     = models.CharField(max_length = 128)
    position = models.CharField(max_length = 256, blank=True)
    user     = models.ForeignKey(User)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Student(models.Model):
    # Although Icelandic kt are all just 10 characters, some schools have students that
    # don't seem to have icelandic kt's. Hence, the 32 char max_length for ssn
    ssn  = models.CharField(max_length = 32, unique=True)
    name = models.CharField(max_length = 128)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


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


class GroupSurvey(models.Model):
    studentgroup = models.ForeignKey(
        'StudentGroup', null=True, blank=True, on_delete=models.SET_NULL
    )
    survey       = models.ForeignKey(Survey)
    active_from  = models.DateField(default=timezone.now)
    active_to    = models.DateField(default=timezone.now)

    def save(self, *args, **kwargs):
        if self.survey:
            self.active_from = self.survey.active_from
            self.active_to   = self.survey.active_to
        super(GroupSurvey, self).save(*args, **kwargs)

    def is_expired(self):
        if timezone.now().date() > self.active_to:
            return True
        return False

    def results(self):
        return SurveyResult.objects.filter(survey=self)

    def __str__(self):
        return self.survey.title


class SurveyResult(models.Model):
    student     = models.ForeignKey('Student')
    created_at  = models.DateTimeField(default=timezone.now)
    results     = models.TextField()
    reported_by = models.ForeignKey(
        'Teacher', null=True, blank=True, on_delete=models.SET_NULL
    )
    survey      = models.ForeignKey(
        'GroupSurvey', null=True, blank=True, on_delete=models.SET_NULL
    )
    created_at  = models.DateField(default=timezone.now)

    @classmethod
    def get_results(cls, id):
        return json.loads(cls(pk=id).results)


class SurveyLogin(models.Model):
    student     = models.ForeignKey(Student)
    survey_id   = models.CharField(max_length = 256)  # external survey identity
    survey_code = models.CharField(max_length = 16)
