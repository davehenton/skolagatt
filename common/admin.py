from django.contrib import admin

import common.models as cm_models

# Register your models here.
register = admin.site.register
register(cm_models.School)
register(cm_models.Manager)
register(cm_models.Teacher)
register(cm_models.Student)
register(cm_models.StudentGroup)
register(cm_models.Survey)
register(cm_models.SurveyResult)