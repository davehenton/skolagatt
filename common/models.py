# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

from django.contrib.auth.models import User
from django.contrib.postgres.fields import JSONField
from django.utils import timezone

import json
from collections import OrderedDict

from froala_editor.fields import FroalaField

from survey.models import Survey

from common.static import (
    STUDENT_YEAR_LIST,
    POST_CODE_LIST,
    MUNICIPALITIES_LIST,
    COUNTRY_PARTS_LIST,
)


class Manager(models.Model):
    ssn = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=128)
    email = models.CharField(max_length=256, blank=True)
    phone = models.CharField(max_length=7, blank=True)
    position = models.CharField(max_length=256, blank=True)
    user = models.ForeignKey(User)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Teacher(models.Model):
    ssn = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=128)
    position = models.CharField(max_length=256, blank=True)
    user = models.ForeignKey(User)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Student(models.Model):
    # Although Icelandic kt are all just 10 characters, some schools have students that
    # don't seem to have icelandic kt's. Hence, the 32 char max_length for ssn
    ssn = models.CharField(max_length=32, unique=True)
    name = models.CharField(max_length=128)

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
    MUNICIPALITIES = MUNICIPALITIES_LIST
    PARTS = COUNTRY_PARTS_LIST
    POST_CODES = POST_CODE_LIST

    name = models.CharField(max_length=128)
    ssn = models.CharField(max_length=10)
    managers = models.ManyToManyField(Manager, blank=True)
    teachers = models.ManyToManyField(Teacher, blank=True)
    students = models.ManyToManyField(Student, blank=True)
    school_nr = models.IntegerField(default=None, blank=True, null=True)

    address = models.CharField(max_length=256, blank=True, null=True)                              # Heimilisfang
    post_code = models.CharField(max_length=3, blank=True, null=True, choices=POST_CODES)          # Póstnúmer
    municipality = models.CharField(max_length=32, blank=True, null=True, choices=MUNICIPALITIES)  # Sveitarfélag
    part = models.CharField(max_length=24, blank=True, null=True, choices=PARTS)                   # Landshluti

    def __str__(self):
        return self.name + " (" + self.ssn + ")"

    def get_school_surveys(self):
        surveys = GroupSurvey.objects.filter(studentgroup__in=self.studentgroup_set.all())
        return surveys

    class Meta:
        ordering = ["name"]


class StudentGroup(models.Model):
    name = models.CharField(max_length=128)
    YEARS = STUDENT_YEAR_LIST
    student_year = models.CharField(max_length=2, choices=YEARS, null=True, blank=True)
    group_managers = models.ManyToManyField(Teacher, blank=True)
    school = models.ForeignKey('School')
    students = models.ManyToManyField(Student, blank=True)

    def __str__(self):
        return self.name


class GroupSurvey(models.Model):
    studentgroup = models.ForeignKey(
        'StudentGroup', null=True, blank=True, on_delete=models.SET_NULL
    )
    survey = models.ForeignKey(Survey)
    active_from = models.DateField(default=timezone.now)
    active_to = models.DateField(default=timezone.now)

    # class Meta:
    #     unique_together = (("studentgroup", "survey"))

    def save(self, *args, **kwargs):
        if self.survey:
            self.active_from = self.survey.active_from
            self.active_to = self.survey.active_to
        super(GroupSurvey, self).save(*args, **kwargs)

    def is_expired(self):
        if timezone.now().date() > self.active_to:
            return True
        return False

    def is_open(self):
        curdate = timezone.now().date()

        if curdate < self.active_to and curdate > self.active_from:
            return True
        else:
            return False

    def results(self):
        return SurveyResult.objects.filter(survey=self)

    def title(self):
        if self.survey:
            return self.survey.title
        else:
            return ""

    def __str__(self):
        return self.survey.title


class SurveyResult(models.Model):
    student = models.ForeignKey('Student', null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(default=timezone.now)
    results = JSONField(null=True, blank=True)
    reported_by = models.ForeignKey('Teacher', null=True, blank=True, on_delete=models.SET_NULL)
    survey = models.ForeignKey('GroupSurvey', null=True, blank=True, on_delete=models.CASCADE)
    created_at = models.DateField(default=timezone.now)

    # class Meta:
    #     unique_together = (("student", "survey"))

    def _clean_lesskimun_sums(self, sums):
        keys = ['hljod', 'mal', 'bok']

        for key in keys:
            sums[key] = sums.pop(key + '_')

    def _lesskimun_input_sums(self):
        '''
        Cycle through input_values, sum up all values where the key starts with
        'hljod_', 'mal_', 'bok_'. Checks for input errors.
        '''
        input_values = self.results['input_values']

        sums = {'hljod_': 0, 'mal_': 0, 'bok_': 0}
        for key, value in input_values.items():
            for type_sum in sums.keys():
                # type = 'hljod_' for instance, type_sum for 'hljod_' starts as 0
                if key.startswith(type_sum):
                    if not str(value).isdigit():
                        # Input error so we will make this type_sum permanently = -1 to indicate error
                        sums[type_sum] = -1
                    elif str(value).isdigit() and not sums[type_sum] == -1:
                        # Not input error so let's add up
                        sums[type_sum] += int(value)

        self._clean_lesskimun_sums(sums)
        return sums

    def _get_lesskimun_level_thresholds(self):
        level_thresholds = OrderedDict()
        level_thresholds['hljod'] = OrderedDict()
        level_thresholds['mal'] = OrderedDict()
        level_thresholds['bok'] = OrderedDict()
        level_thresholds['hljod']['Áhætta 1'] = 14
        level_thresholds['hljod']['Áhætta 2'] = 17
        level_thresholds['hljod']['Óvissa'] = 19
        level_thresholds['mal']['Áhætta 1'] = 14
        level_thresholds['mal']['Áhætta 2'] = 16
        level_thresholds['mal']['Óvissa'] = 17
        level_thresholds['bok']['Áhætta 1'] = 7
        level_thresholds['bok']['Áhætta 2'] = 10
        level_thresholds['bok']['Óvissa'] = 12

        return level_thresholds

    def _apply_lesskimun_thresholds(self, the_sum, thresholds):
        if the_sum == -1:
            return 'Vantar gögn'

        for label, threshold in thresholds.items():
            if the_sum <= threshold:
                return label
        return 'Utan áhættu'

    def _get_lesskimun_levels(self, sums):
        level_thresholds = self._get_lesskimun_level_thresholds()
        output = []

        for key in level_thresholds.keys():
            level = self._apply_lesskimun_thresholds(sums[key], level_thresholds[key])
            output.append(level)
        return output

    def _lesskimun_results(self):
        sums = self._lesskimun_input_sums()

        return self._get_lesskimun_levels(sums)

    def _lesfimi_get_errors(self, click_values):
        errors = len(click_values) - 1

        if errors < 3:
            return 0
        elif errors < 10:
            return errors - 2
        else:
            return (2 * errors) - 11

    def _lesfimi_results(self, transformation):
        click_values = self.results['click_values']
        try:
            errors = self._lesfimi_get_errors(click_values)

            last_word_num = int(click_values[-1].split(',')[0])
            vegin_oam = last_word_num - errors
            vegin_oam = int(round(vegin_oam / 2))

            if (transformation):
                data = transformation.data
                key = str(vegin_oam)
                if key in data:
                    vegin_oam = data[key]

            vegin_oam = max(0, vegin_oam)

            return [vegin_oam]
        except:
            return [""]

    def calculated_results(self, use_transformation=True):
        survey_type = self.survey.survey.survey_type.title

        if survey_type == 'Lesskimun':
            return self._lesskimun_results()
        elif survey_type == 'Lesfimi':
            transformation = None
            if use_transformation:
                if self.survey.survey.surveytransformation_set.exists():
                    transformation = self.survey.survey.surveytransformation_set.first()
            return self._lesfimi_results(transformation)
        else:
            return self.results['click_values']

    @classmethod
    def get_results(cls, id):
        return json.loads(cls(pk=id).results)


class SurveyLogin(models.Model):
    student = models.ForeignKey(Student)
    survey_id = models.CharField(max_length=256)  # external survey identity
    survey_code = models.CharField(max_length=16)


# Prófadæmi, spurningar
class ExampleSurveyQuestion(models.Model):
    quiz_type_choices = (
        ('STÆ', 'Stærðfræði'),
        ('ENS', 'Enska'),
        ('ÍSL', 'Íslenska'),
    )
    category_choices = (
        ('RA', 'Reikningur og aðgerðir'),
        ('RM', 'Rúmfræði'),
        ('TT', 'Tölur og talnaskilningur'),
        ('AL', 'Algebra'),
        ('HP', 'Hlutföll og prósentur'),
        ('LE', 'Lesskilningur'),
        ('MN', 'Málnotkun'),
    )
    created_by = models.ForeignKey(User, null=True)
    # flýtikóði
    quickcode = models.CharField(max_length=16, unique=True)
    # próftegund
    quiz_type = models.CharField(max_length=3, choices=quiz_type_choices)
    # flokkur
    category = models.CharField(max_length=2, choices=category_choices)
    # ĺýsing
    description = models.TextField()
    # dæmi
    example = FroalaField()

    def answers_total(self):
        return self.examplesurveyanswer_set.count()

    def answers_correct_pct(self):
        answers_total = self.answers_total()

        if answers_total == 0:
            return "0%"
        answers_correct = self.examplesurveyanswer_set.filter(answer=True).count()

        return "{:.1f}%".format((answers_correct / answers_total) * 100)


# Prófadæmi, svör
class ExampleSurveyAnswer(models.Model):
    # nemandi
    student = models.ForeignKey(Student)
    # spurning
    question = models.ForeignKey(ExampleSurveyQuestion)
    # próf
    groupsurvey = models.ForeignKey(GroupSurvey, null=True)
    exam_code = models.CharField(max_length=128, null=True)
    # dags
    date = models.DateField(default=timezone.now)
    # Svar (rétt/rangt)
    answer = models.BooleanField()
