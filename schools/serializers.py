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
        fields = ('student', 'survey', 'results')

    def to_representation(self, instance):
        data = super(SurveyResultSerializer, self).to_representation(instance)
        data['results'] = json.loads(data['results'])
        return data

class SchoolSerializer(serializers.ModelSerializer):
    survey_results = serializers.SerializerMethodField('school_survey_results')
    class Meta:
        model = School
        fields = ('name', 'ssn', 'survey_results')

    def school_survey_results(self, container):
        school_student_groups = StudentGroup.objects.filter(school=container)
        school_surveys = Survey.objects.filter(studentgroup=school_student_groups)
        data = SurveyResult.objects.filter(survey=school_surveys)
        serializer = SurveyResultSerializer(instance=data, many=True)
        return serializer.data