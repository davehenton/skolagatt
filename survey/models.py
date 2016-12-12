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

    def __str__(self):
        return self.title


class SurveyResource(models.Model):
    survey       = models.ForeignKey(Survey)
    title        = models.CharField(max_length=128)
    resource_url = models.CharField(max_length=1024)
    description  = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.title


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
    identifier  = models.CharField(max_length=32)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.title


class SurveyInputField(models.Model):
    input_group = models.ForeignKey(SurveyInputGroup)
    name        = models.CharField(max_length=128)
    label       = models.CharField(max_length=128)

    def __str__(self):
        return self.input_group.title + ': ' + self.name


class SurveyAttendance(models.Model):
    survey = models.ForeignKey(Survey)
    student = models.ForeignKey(Student)
    attendance = models.IntegerField()

    def __str__(self):
        return self.student.name + ': ' + self.survey.title


class SurveyException(models.Model):
    survey      = models.ForeignKey(Survey)
    student     = models.ForeignKey(Student)
    description = models.CharField(max_length=1024, null=True, blank=True)

    def __str__(self):
        return self.student.name + ': ' + self.survey.title


class SurveySupportType(models.Model):
    support_type = models.CharField(max_length=128)
    description  = models.CharField(max_length=1024, null=True, blank=True)

    def __str__(self):
        return self.title


class SurveySupport(models.Model):
    survey      = models.ForeignKey(Survey)
    student     = models.ForeignKey(Student)
    support     = models.ForeignKey(SurveySupportType)
    description = models.CharField(max_length=1024, null=True, blank=True)

    def __str__(self):
        return self.student.name + ': ' + self.survey.title
