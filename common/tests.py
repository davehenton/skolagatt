from django.test import TestCase

# Create your tests here.
from .models import *
from survey.models import (
    Survey,
    SurveyType,
)


class SurveyResultCalculatedResultsTests(TestCase):
    fixtures = ['common']

    def setUp(self):
        self.surveys = []
        self.groupsurveys = []
        self.surveyresults = []
        survey = Survey.objects.get(identifer='test_test_1')

        groupsurveys.append(GroupSurvey.objects.create(
            survey=survey,
        ))
        self.surveyresults.append(
            SurveyResult.create(
                survey=groupsurvey,
                results={
                    'click_values': [
                        '1,test1',
                        '11,test2',
                        '21,test3',
                    ],
                    'input_values': [
                    ],
                }
            ))
        
