from django.test import TestCase

# Create your tests here.
from .models import *
from survey.models import (
    Survey,
    SurveyType,
)


class SurveyResultLesfimiCalculatedResultsTests(TestCase):
    fixtures = ['auth', 'contenttypes', 'common']

    def setUp(self):
        self.groupsurveys = []
        self.surveyresults = []
        self.school = School.objects.first()
        self.studentgroup1 = self.school.studentgroup_set.all()[0]
        self.student1 = self.studentgroup1.students.all()[0]
        self.student2 = self.studentgroup1.students.all()[1]
        self.student3 = self.studentgroup1.students.all()[2]

        self.survey_type = SurveyType.objects.create(
            identifier='b1_LF',
            title='Lesfimi',
        )
        self.survey1 = Survey.objects.create(
            identifier='test_test_1',
            survey_type=self.survey_type,
            student_year=self.studentgroup1.student_year,
            created_by_id=1,
        )

        self.groupsurveys.append(GroupSurvey.objects.create(
            survey=self.survey1,
            studentgroup=self.studentgroup1,
        ))

        self.surveyresults.append(
            SurveyResult.objects.create(
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
