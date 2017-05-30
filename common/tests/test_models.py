# -*- coding: utf-8 -*-
from django.test import TestCase

from ..models import (
    School,
    GroupSurvey,
    SurveyResult,
)

from survey.models import (
    Survey,
    SurveyType,
    SurveyTransformation,
)

# Tests for common.models


class SurveyResultLesfimiCalculatedResultsTests(TestCase):
    fixtures = ['auth', 'common']

    def setUp(self):
        super(SurveyResultLesfimiCalculatedResultsTests, self).setUp()
        self.school = School.objects.first()
        self.studentgroup1 = self.school.studentgroup_set.all()[0]
        self.students1 = self.studentgroup1.students.all()

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

    def _gen_clicked_words(self, num):
        click_values = []
        for i in range(1, num + 1):
            click_values.append('{},word{}'.format(i, i))

        return click_values

    def test_lesfimi_calculated_results_2_errors_21_words_no_transformation_eq_10(self):
        click_values = self._gen_clicked_words(2)  # Generate 2 wrong words
        click_values.append('21,word21')  # Add the last word
        obj = SurveyResult(
            survey=self.groupsurvey1,
            student=self.students1[0],
            results={
                'click_values': click_values,
                'input_values': [],
            }
        )
        calculated_results = obj.calculated_results()
        self.assertEqual(len(calculated_results), 1)
        self.assertEqual(int(calculated_results[0]), 10)

    def test_lesfimi_calculated_results_returns_integer(self):
        click_values = []
        click_values.append('20, word20')
        obj = SurveyResult(
            survey=self.groupsurvey1,
            student=self.students1[0],
            results={
                'click_values': click_values,
                'input_values': [],
            }
        )
        calculated_results = obj.calculated_results()
        self.assertTrue(isinstance(calculated_results[0], int))

    def test_lesfimi_calculated_results_20_errors_100_words_no_transformation_eq_36(self):
        click_values = self._gen_clicked_words(20)  # Generate 20 wrong words
        click_values.append('100,word100')  # Add the last word

        obj = SurveyResult(
            survey=self.groupsurvey1,
            student=self.students1[1],
            results={
                'click_values': click_values,
                'input_values': [],
            }
        )
        calculated_results = obj.calculated_results()
        self.assertEqual(len(calculated_results), 1)
        self.assertEqual(int(calculated_results[0]), 36)

    def test_lesfimi_calculated_results_9_errors_99_words_no_transformation_eq_46(self):
        click_values = self._gen_clicked_words(9)  # Generate 9 wrong words
        click_values.append('99,word99')  # Add the last word

        obj = SurveyResult(
            survey=self.groupsurvey1,
            student=self.students1[2],
            results={
                'click_values': click_values,
                'input_values': [],
            }
        )

        calculated_results = obj.calculated_results()
        self.assertEqual(len(calculated_results), 1)
        self.assertEqual(int(calculated_results[0]), 46)

    def test_lesfimi_calculated_results_with_transformation_of_100_to_79(self):
        obj = SurveyResult(
            survey=self.groupsurvey2,
            student=self.students1[3],
            results={
                'click_values': [
                    '200,test',
                ],
                'input_values': [
                ],
            }
        )
        calculated_results = obj.calculated_results()
        self.assertEqual(len(calculated_results), 1)
        self.assertEqual(int(calculated_results[0]), 79)
