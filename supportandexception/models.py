# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.db import models

from common.models  import Student, Manager, GroupSurvey

from rest_framework import serializers


class StudentExceptionSupport(models.Model):
    student     = models.ForeignKey(Student)
    groupsurvey = models.ForeignKey(GroupSurvey, null=True)


# undanþágur
class Exceptions(models.Model):
    student             = models.ForeignKey(Student)
    groupsurvey         = models.ForeignKey(GroupSurvey, null=True)
    exempt              = models.BooleanField(default=False)
    exceptionssignature = models.ForeignKey(Manager)
    exceptionsdate      = models.DateField(auto_now=False, auto_now_add=True, null=True)


# Stuðningsúrræði

class SupportResource(models.Model):
    student                  = models.ForeignKey(Student)
    groupsurvey              = models.ForeignKey(GroupSurvey, null=True)
    supportresourcesignature = models.ForeignKey(Manager)
    supportresourcedate      = models.DateField(auto_now = True, null = True)
    reading_assistance       = models.BooleanField(default=False)
    interpretation           = models.BooleanField(default=False)
    longer_time              = models.BooleanField(default=False)



# serializer
class ExceptionsSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Exceptions
        fields = (
            'exempt',
            'exceptionssignature',
            'exceptionsdate'
        )


class SupportResourceSerializer(serializers.ModelSerializer):
    class Meta:
        model  = SupportResource
        fields = (
            'supportresourcesignature',
            'supportresourcedate',
            'support_title',
            'reading_assistance',
            'interpretation',
            'longer_time'
        )


class StudentExceptionSerializer(serializers.ModelSerializer):
    class Meta:
        model  = StudentExceptionSupport
        fields = ('student', 'notes')


class StudentWithExceptSerializer(serializers.ModelSerializer):
    excep        = serializers.SerializerMethodField('get_exceptions')
    support      = serializers.SerializerMethodField('get_supportresource')
    studentexcep = serializers.SerializerMethodField('get_studentexceptionsupport')

    class Meta:
        model  = Student
        fields = ('ssn', 'name', 'studentexcep', 'excep', 'support')

    def get_exceptions(self, container):
        data       = Exceptions.objects.filter(student=container)
        serializer = ExceptionsSerializer(instance=data, many=True)
        return serializer.data

    def get_supportresource(self, container):
        data       = SupportResource.objects.filter(student=container)
        serializer = SupportResourceSerializer(instance=data, many=True)
        return serializer.data

    def get_studentexceptionsupport(self, container):
        data       = StudentExceptionSupport.objects.filter(student=container)
        serializer = StudentExceptionSerializer(instance=data, many=True)
        return serializer.data
