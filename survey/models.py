from django.contrib.auth.models import User
from django.db                  import models
from django.utils               import timezone


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
    YEARS       = (
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
    student_year                   = models.CharField(max_length = 2, choices=YEARS, null=True, blank=True)
    description                    = models.TextField()
    created_at                     = models.DateTimeField(default=timezone.now)
    active_from                    = models.DateField(default=timezone.now)
    active_to                      = models.DateField(default=timezone.now)
    created_by                     = models.ForeignKey(User)
    old_version                    = models.ForeignKey('Survey', null=True, blank=True)
    support_and_exception_deadline = models.DateField(default=timezone.now)

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
    title = models.CharField(max_length=32)
    md    = models.TextField(null=True, blank=True)
    info  = models.TextField()


class SurveyInputGroup(models.Model):
    survey      = models.ForeignKey(Survey)
    title       = models.CharField(max_length=128)
    identifier  = models.CharField(max_length=32)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.title

    def input_fields(self):
        inputfields = SurveyInputField.objects.filter(input_group=self).order_by('name')
        return inputfields

    def num_input_fields(self):
        return len(self.input_fields())


class SurveyInputField(models.Model):
    input_group = models.ForeignKey(SurveyInputGroup)
    name        = models.CharField(max_length=128)
    label       = models.CharField(max_length=128)

    def get_id(self):
        return self.input_group.identifier + '_' + self.name

    def __str__(self):
        return self.input_group.title + ': ' + self.get_id()
