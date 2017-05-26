from django.test import TestCase

from .models import *
from survey.models import (
    Survey,
    SurveyType,
    SurveyTransformation,
)


class SurveyResultLesfimiCalculatedResultsTests(TestCase):
    fixtures = ['auth', 'common']

    def setUp(self):
        self.surveyresults1 = []
        self.surveyresults2 = []
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
        self.survey2 = Survey.objects.create(
            identifier='test_test_2',
            survey_type=self.survey_type,
            student_year=self.studentgroup1.student_year,
            created_by_id=1,
        )
        self.surveytransformation1 = SurveyTransformation.objects.create(
            survey=self.survey2,
            name='vs',
            order=1,
            unit='Vegin orð á mínútu',
            data={
                '100': 79.0,
            }
        )

        self.groupsurvey1 = GroupSurvey.objects.create(
            survey=self.survey1,
            studentgroup=self.studentgroup1,
        )
        self.groupsurvey2 = GroupSurvey.objects.create(
            survey=self.survey2,
            studentgroup=self.studentgroup1,
        )

        self.surveyresults1.append(
            SurveyResult.objects.create(
                survey=self.groupsurvey1,
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
        self.surveyresults1.append(
            SurveyResult.objects.create(
                survey=self.groupsurvey1,
                student=self.student2,
                results={
                    'click_values': [
                        '1,test1', '2,test2', '3,test3', '4,test4', '5,test5', '6,test6', '7,test7', '8,test8',
                        '9,test9', '10,test10', '11,test11', '12,test12', '13,test13', '14,test14', '15,test15',
                        '16,test16', '17,test17', '18,test18', '19,test19', '20,test20', '100,test10'
                    ],
                    'input_values': [
                    ],
                }
            ))
        self.surveyresults1.append(
            SurveyResult.objects.create(
                survey=self.groupsurvey1,
                student=self.student2,
                results={
                    'click_values': [
                        '1,test1', '2,test2', '3,test3', '4,test4', '5,test5', '6,test6', '7,test7', '8,test8',
                        '9,test9', '99,test10'
                    ],
                    'input_values': [
                    ],
                }
            ))
        self.surveyresults2.append(
            SurveyResult.objects.create(
                survey=self.groupsurvey2,
                student=self.student3,
                results={
                    'click_values': [
                        '200,test',
                    ],
                    'input_values': [
                    ],
                }))

    def test_lesfimi_calculated_results_2_errors_21_words_no_transformation(self):
        calculated_results = self.surveyresults1[0].calculated_results()
        self.assertEqual(len(calculated_results), 1)
        self.assertEqual(int(calculated_results[0]), 10)

    def test_lesfimi_calculated_results_20_errors_100_words_no_transformation(self):
        calculated_results = self.surveyresults1[1].calculated_results()
        self.assertEqual(len(calculated_results), 1)
        self.assertEqual(int(calculated_results[0]), 36)

    def test_lesfimi_calculated_results_9_errors_99_words_no_transformation(self):
        calculated_results = self.surveyresults1[2].calculated_results()
        self.assertEqual(len(calculated_results), 1)
        self.assertEqual(int(calculated_results[0]), 46)

    def test_lesfimi_calculated_results_with_transformation_of_100_to_79(self):
        calculated_results = self.surveyresults2[0].calculated_results()
        self.assertEqual(len(calculated_results), 1)
        self.assertEqual(int(calculated_results[0]), 79)