from common.models import *
from rest_framework import serializers
import json

class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = ('name', 'ssn')

class SurveyResultSerializer(serializers.ModelSerializer):
    student = StudentSerializer()
    class Meta:
        model = SurveyResult
        fields = ('student', 'results')

    def to_representation(self, instance):
        data = super(SurveyResultSerializer, self).to_representation(instance)
        data['results'] = json.loads(data['results'])
        return data

class SurveySerializer(serializers.ModelSerializer):
    results = SurveyResultSerializer(many=True)
    class Meta:
        model = Survey
        fields = ('survey', 'results')

class SchoolSerializer(serializers.ModelSerializer):
    surveys = serializers.SerializerMethodField('school_surveys')
    class Meta:
        model = School
        fields = ('name', 'ssn', 'surveys')

    def school_surveys(self, container):
        school_student_groups = StudentGroup.objects.filter(school=container)
        school_surveys = Survey.objects.filter(studentgroup=school_student_groups)
        serializer = SurveySerializer(instance=school_surveys, many=True)
        return serializer.data