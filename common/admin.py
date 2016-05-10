from django.contrib import admin

from .models import *
# Register your models here.
register = admin.site.register
register(School)
register(Manager)
register(Teacher)
register(Student)
register(StudentGroup)
register(Survey)
register(SurveyResult)