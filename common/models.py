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

    def __str__(self):
        return self.notification_type


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

    def get_distinct_surveys(self):
        groups = self.studentgroup_set.all().values_list('groupsurvey__pk', flat=True)
        surveys = GroupSurvey.objects.filter(pk__in=[x for x in groups if x is not None]).distinct()
        return surveys

    def get_distinct_survey_results(self):
        return self.surveyresult_set.all()

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

    def get_school_surveys(self):
        surveys = GroupSurvey.objects.filter(studentgroup__in=self.studentgroup_set.all())
        return surveys

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


# Prófadæmi, spurningar
class ExampleSurveyQuestion(models.Model):
    # flýtikóði
    quickcode = models.CharField(max_length = 16, unique=True)
    # próftegund
    quiz_type = models.CharField(max_length = 3)
    # flokkur
    category = models.CharField(max_length = 2)
    # ĺýsing
    description = models.TextField()
    # dæmi
    example = models.TextField()


# Prófadæmi, svör
class ExampleSurveyAnswer(models.Model):
    # nemandi
    student = models.ForeignKey(Student)
    # spurning
    question = models.ForeignKey(ExampleSurveyQuestion)
    # próf
    groupsurvey = models.ForeignKey(GroupSurvey)
    # Svar (rétt/rangt)
    answer = models.BooleanField()
