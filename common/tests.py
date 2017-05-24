from django.test import TestCase

# Create your tests here.
from .models import *
from survey.models import (
    Survey,
    SurveyType,
)


class SurveyResultLesfimiCalculatedResultsTests(TestCase):
    fixtures = ['common']

    def setUp(self):
        self.groupsurveys = []
        self.surveyresults = []
        self.survey = Survey.objects.create(
            identifer='test_test_1',
            survey_type=SurveyType.objects.create(
                identifier='b1_LF',
                title='Lesfimi',
            )
        )
        self.school = School.objects.first()
        self.studentgroup = school.studentgroup_set.first()
        self.student1 = studentgroup.student_set.all()[0]
        self.student2 = studentgroup.student_set.all()[1]
        self.student3 = studentgroup.student_set.all()[2]
        self.groupsurveys.append(GroupSurvey.objects.create(
            survey=self.survey,
            studentgroup=self.studentgroup,
        ))
        self.surveyresults.append(
            SurveyResult.create(
                survey=self.groupsurveys[0],
                student=self.student1,
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

    def test_lesfimi_calculated_results(self):
        calculated_results = self.surveyresults[0].calculated_results()
        self.assertEqual(len(calculated_results), 1)
        self.assertEqual(int(calculated_results[0]), 34)
