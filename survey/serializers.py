from .              import models
from rest_framework import serializers


class SurveyInputFieldSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model  = models.SurveyInputField
        fields = ('name', 'label', 'description')


class SurveyGradingTemplateSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model  = models.SurveyGradingTemplate
        fields = ('md', 'info')


class SurveyResourceSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model  = models.SurveyResource
        fields = ('title', 'resource_url', 'description')


class SurveySerializer(serializers.ModelSerializer):
    texts            = serializers.SerializerMethodField('get_survey_texts')
    resources        = serializers.SerializerMethodField('get_survey_resources')
    grading_template = serializers.SerializerMethodField('get_survey_grading_template')
    input_fields     = serializers.SerializerMethodField()

    class Meta:
        model  = models.Survey
        fields = [
            'pk', 'identifier', 'title', 'description', 'active_from',
            'active_to', 'texts', 'resources', 'grading_template', 'input_fields'
        ]

    def get_survey_data(self, container):
        data       = models.SurveyData.objects.filter(survey=container)
        serializer = SurveyDataSerializer(instance=data, many=True)
        return serializer.data

    def get_survey_resources(self, container):
        data       = models.SurveyResource.objects.filter(survey=container)
        serializer = SurveyResourceSerializer(instance=data, many=True)
        return serializer.data

    def get_survey_grading_template(self, container):
        data       = models.SurveyGradingTemplate.objects.filter(survey=container)
        serializer = SurveyGradingTemplateSerializer(instance=data, many=True)
        return serializer.data

    def get_input_fields(self, container):
        data       = models.SurveyInputField.objects.filter(survey=container)
        serializer = SurveyInputFieldSerializer(instance=data, many=True)
        return serializer.data
