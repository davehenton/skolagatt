# -*- coding: utf-8 -*-
from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from django.contrib.postgres.fields import JSONField

from common.static import STUDENT_YEAR_LIST

from froala_editor.fields import FroalaField


class SurveyType(models.Model):
    """docstring for SurveyType"""
    identifier = models.CharField(max_length=64)
    title = models.CharField(max_length=128)
    description = models.CharField(max_length=1024, default='', blank=True)

    def __str__(self):
        return self.title


class Survey(models.Model):
    identifier = models.CharField(max_length=128)
    title = models.CharField(max_length=256)
    survey_type = models.ForeignKey(SurveyType)
    YEARS = STUDENT_YEAR_LIST
    student_year = models.CharField(max_length=2, default='', choices=YEARS)
    description = FroalaField()
    created_at = models.DateTimeField(default=timezone.now)
    active_from = models.DateField(default=timezone.now)
    active_to = models.DateField(default=timezone.now)
    created_by = models.ForeignKey(User)
    old_version = models.ForeignKey('Survey', null=True, blank=True)
    survey_family_id = models.CharField(max_length=36, default='', blank=True)

    def __str__(self):
        return self.title


class SurveyResource(models.Model):
    survey = models.ForeignKey(Survey)
    title = models.CharField(max_length=128)
    resource_url = models.CharField(max_length=1024, null=True, blank=True)
    description = FroalaField(null=True, blank=True)
    resource_html = FroalaField(null=True, blank=True)

    def __str__(self):
        return self.title


class SurveyGradingTemplate(models.Model):
    survey = models.OneToOneField(
        Survey,
        on_delete=models.CASCADE,
    )
    title = models.CharField(max_length=32)
    md = models.TextField(null=True, blank=True)
    info = models.TextField()


class SurveyInputGroup(models.Model):
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE)
    title = models.CharField(max_length=128)
    identifier = models.CharField(max_length=32)
    description = models.TextField(default='', blank=True)

    def __str__(self):
        return self.title

    def input_fields(self):
        return self.surveyinputfield_set.order_by('name').all()

    def num_input_fields(self):
        return len(self.surveyinputfield_set.all())


class SurveyInputField(models.Model):
    input_group = models.ForeignKey(SurveyInputGroup, on_delete=models.CASCADE)
    name = models.CharField(max_length=128)
    label = models.CharField(max_length=128)
    default_value = models.CharField(max_length=128, default='', blank=True)

    def get_id(self):
        return self.input_group.identifier + '_' + self.name

    def __str__(self):
        return self.input_group.title + ': ' + self.get_id()


# Vörpunartafla
class SurveyTransformation(models.Model):
    survey = models.ForeignKey(Survey)
    name = models.CharField(max_length=128)
    order = models.IntegerField()
    data = JSONField()
    unit = models.CharField(max_length=60, null=True)

    def __str__(self):
        return self.name
