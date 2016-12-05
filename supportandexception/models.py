# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.db import models

from common.models  import Student, Manager
from rest_framework import serializers


class StudentExceptionSupport(models.Model):
    student = models.ForeignKey(Student)
    notes   = models.CharField(max_length = 500)


# undanþágur
class Exceptions(models.Model):
    student             = models.ForeignKey(Student)
    reason              = models.CharField(max_length = 1)
    exam                = models.CharField(max_length = 1)
    explanation         = models.CharField(max_length = 500)
    exceptionssignature = models.ForeignKey(Manager)
    exceptionsdate      = models.DateField(auto_now=False, auto_now_add=True, null=True)

    def __str__(self):
        return self.reason


# Stuðningsúrræði

class SupportResource(models.Model):
    student                  = models.ForeignKey(Student)
    explanation              = models.CharField(max_length = 500)
    supportresourcesignature = models.ForeignKey(Manager)
    supportresourcedate      = models.DateField(auto_now = True, null = True)
    support_title            = models.CharField(max_length = 1, null=True)
    reading_assistance       = models.CharField(max_length = 1, null=True)
    interpretation           = models.CharField(max_length = 1, null=True)
    longer_time              = models.CharField(max_length = 1, null=True)

    def __str__(self):
        return self.explanation


# serializer
class ExceptionsSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Exceptions
        fields = (
            'reason',
            'exam',
            'explanation',
            'exceptionssignature',
            'exceptionsdate'
        )


class SupportResourceSerializer(serializers.ModelSerializer):
    class Meta:
        model  = SupportResource
        fields = (
            'explanation',
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
