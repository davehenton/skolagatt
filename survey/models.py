from django.contrib.auth.models import User
from django.db                  import models
from django.utils               import timezone
from common.models              import Student


class SurveyType(models.Model):
    """docstring for SurveyType"""
    identifier  = models.CharField(max_length = 64)
    title       = models.CharField(max_length = 128)
    description = models.CharField(max_length = 1024, null=True, blank=True)

    def __str__(self):
        return self.title


class Survey(models.Model):
    identifier  = models.CharField(max_length = 128)
    title       = models.CharField(max_length = 256)
    survey_type = models.ForeignKey(SurveyType)
    description = models.TextField()
    created_at  = models.DateTimeField(default=timezone.now)
    active_from = models.DateField(default=timezone.now)
    active_to   = models.DateField(default=timezone.now)
    created_by  = models.ForeignKey(User)
    old_version = models.ForeignKey('Survey', null=True, blank=True)


class SurveyText(models.Model):
    survey = models.ForeignKey(Survey)
    title  = models.CharField(max_length=128)
    text   = models.TextField(null=True, blank=True)


class SurveyResource(models.Model):
    survey       = models.ForeignKey(Survey)
    title        = models.CharField(max_length=128)
    resource_url = models.CharField(max_length=1024)
    description  = models.TextField(null=True, blank=True)


class SurveyGradingTemplate(models.Model):
    survey = models.OneToOneField(
        Survey,
        on_delete=models.CASCADE,
    )
    md   = models.TextField()
    info = models.TextField()


class SurveyInputGroup(models.Model):
    survey      = models.ForeignKey(Survey)
    title       = models.CharField(max_length=128)
    description = models.TextField(null=True, blank=True)


class SurveyInputField(models.Model):
    input_group = models.ForeignKey(SurveyInputGroup)
    name        = models.CharField(max_length=128)
    label       = models.CharField(max_length=128)


class SurveyAttendance(models.Model):
    survey = models.ForeignKey(Survey)
    student = models.ForeignKey(Student)
    attendance = models.IntegerField()


class SurveyException(models.Model):
    survey      = models.ForeignKey(Survey)
    student     = models.ForeignKey(Student)
    description = models.CharField(max_length=1024, null=True, blank=True)


class SurveySupportType(models.Model):
    support_type = models.CharField(max_length=128)
    description  = models.CharField(max_length=1024, null=True, blank=True)


class SurveySupport(models.Model):
    survey      = models.ForeignKey(Survey)
    student     = models.ForeignKey(Student)
    support     = models.ForeignKey(SurveySupportType)
    description = models.CharField(max_length=1024, null=True, blank=True)
