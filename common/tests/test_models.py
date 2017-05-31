# -*- coding: utf-8 -*-
from django.test import TestCase, mock

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


class SurveyResultLesskimunCalculatedResultsTests(TestCase):
    fixtures = ['auth', 'common']

    def setUp(self):
        super(SurveyResultLesskimunCalculatedResultsTests, self).setUp()
        self.school = School.objects.first()
        self.studentgroup1 = self.school.studentgroup_set.all()[0]
        self.students1 = self.studentgroup1.students.all()

        self.survey_type = SurveyType.objects.create(
            identifier='b1_LE',
            title='Lesskimun',
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

    def test_clean_lesskimun_sums(self):
        obj = SurveyResult()
        input_dict = {'hljod_': 1, 'bok_': 2, 'mal_': 3}
        expected_output = {'hljod': 1, 'bok': 2, 'mal': 3}
        obj._clean_lesskimun_sums(input_dict)
        self.assertEqual(input_dict, expected_output)

    def test_lesskimun_input_sums_hljod(self):
        obj = SurveyResult(results=dict(input_values=dict(hljod_1=1, hljod_2=2)))
        ret = obj._lesskimun_input_sums()
        self.assertEqual(ret, {'hljod': 1 + 2, 'bok': 0, 'mal': 0})

    def test_lesskimun_input_sums_bok(self):
        obj = SurveyResult(results=dict(input_values=dict(bok_1=1, bok_2=2)))
        ret = obj._lesskimun_input_sums()
        self.assertEqual(ret, {'hljod': 0, 'bok': 1 + 2, 'mal': 0})

    def test_lesskimun_input_sums_mal(self):
        obj = SurveyResult(results=dict(input_values=dict(mal_1=1, mal_2=2)))
        ret = obj._lesskimun_input_sums()
        self.assertEqual(ret, {'hljod': 0, 'bok': 0, 'mal': 1 + 2})

    def test_lesskimun_input_sums_negative_on_wrong_input(self):
        obj = SurveyResult(results=dict(input_values=dict(
            hljod_1=1, hljod_2='', bok_1='', mal_1='', mal_2=2
        )))
        ret = obj._lesskimun_input_sums()
        self.assertEqual(ret, {'hljod': -1, 'bok': -1, 'mal': -1})

    def test_lesskimun_input_sums_wrong_input_on_one_doesnt_affect_others(self):
        obj = SurveyResult(results=dict(input_values=dict(
            hljod_1=1, hljod_2=2, bok_1='', mal_1=4, mal_2=5
        )))
        ret = obj._lesskimun_input_sums()
        self.assertEqual(ret, {'hljod': 1 + 2, 'bok': -1, 'mal': 4 + 5})

    def test_lesskimun_calculated_results_returns_missing_data_when_missing_data(self):
        obj = SurveyResult(
            survey=self.groupsurvey1,
            student=self.students1[0],
            results={
                'click_values': [],
                'input_values': {},
            }
        )
        calculated_results = obj.calculated_results()
        self.assertEqual(len(calculated_results), 3)
        # self.assertEqual(calculated_results, ['Vantar gögn', 'Vantar gögn', 'Vantar gögn'])

    @mock.patch.object(SurveyResult, '_lesskimun_input_sums')
    def test_lesskimun_calculated_results_returns_missing_data_on_malformed_data(self, myMock):
        obj = SurveyResult(survey=self.groupsurvey1, student=self.students1[0])
        myMock.return_value = {'hljod': -1, 'mal': -1, 'bok': -1}
        ret = obj.calculated_results()
        myMock.assert_called_once_with()
        self.assertEqual(len(ret), 3)
        self.assertEqual(ret, ['Vantar gögn', 'Vantar gögn', 'Vantar gögn'])

    @mock.patch.object(SurveyResult, '_lesskimun_input_sums')
    def test_lesskimun_calculated_results_returns_ahaetta_1_for_0_to_14_in_hljod(self, myMock):
        expect = ['Áhætta 1', 'Vantar gögn', 'Vantar gögn']
        obj = SurveyResult(survey=self.groupsurvey1, student=self.students1[0])
        myMock.return_value = {'hljod': 0, 'mal': -1, 'bok': -1}
        ret = obj.calculated_results()
        myMock.assert_called_once_with()
        self.assertEqual(ret, expect)
        myMock.reset_mock()
        myMock.return_value = {'hljod': 14, 'mal': -1, 'bok': -1}
        ret = obj.calculated_results()
        myMock.assert_called_once_with()
        self.assertEqual(ret, expect)

    @mock.patch.object(SurveyResult, '_lesskimun_input_sums')
    def test_lesskimun_calculated_results_returns_ahaetta_1_for_0_to_14_in_mal(self, myMock):
        expect = ['Vantar gögn', 'Áhætta 1', 'Vantar gögn']
        obj = SurveyResult(survey=self.groupsurvey1, student=self.students1[0])
        myMock.return_value = {'hljod': -1, 'mal': 0, 'bok': -1}
        ret = obj.calculated_results()
        myMock.assert_called_once_with()
        self.assertEqual(ret, expect)
        myMock.reset_mock()
        myMock.return_value = {'hljod': -1, 'mal': 14, 'bok': -1}
        ret = obj.calculated_results()
        myMock.assert_called_once_with()
        self.assertEqual(ret, expect)

    @mock.patch.object(SurveyResult, '_lesskimun_input_sums')
    def test_lesskimun_calculated_results_returns_ahaetta_1_for_0_to_7_in_bok(self, myMock):
        expect = ['Vantar gögn', 'Vantar gögn', 'Áhætta 1']
        obj = SurveyResult(survey=self.groupsurvey1, student=self.students1[0])
        myMock.return_value = {'hljod': -1, 'mal': -1, 'bok': 0}
        ret = obj.calculated_results()
        myMock.assert_called_once_with()
        self.assertEqual(ret, expect)
        myMock.reset_mock()
        myMock.return_value = {'hljod': -1, 'mal': -1, 'bok': 7}
        ret = obj.calculated_results()
        myMock.assert_called_once_with()
        self.assertEqual(ret, expect)

    @mock.patch.object(SurveyResult, '_lesskimun_input_sums')
    def test_lesskimun_calculated_results_returns_ahaetta_2_for_15_to_17_in_hljod(self, myMock):
        expect = ['Áhætta 2', 'Vantar gögn', 'Vantar gögn']
        obj = SurveyResult(survey=self.groupsurvey1, student=self.students1[0])
        myMock.return_value = {'hljod': 15, 'mal': -1, 'bok': -1}
        ret = obj.calculated_results()
        myMock.assert_called_once_with()
        self.assertEqual(ret, expect)
        myMock.reset_mock()
        myMock.return_value = {'hljod': 17, 'mal': -1, 'bok': -1}
        ret = obj.calculated_results()
        myMock.assert_called_once_with()
        self.assertEqual(ret, expect)

    @mock.patch.object(SurveyResult, '_lesskimun_input_sums')
    def test_lesskimun_calculated_results_returns_ahaetta_2_for_15_to_16_in_mal(self, myMock):
        expect = ['Vantar gögn', 'Áhætta 2', 'Vantar gögn']
        obj = SurveyResult(survey=self.groupsurvey1, student=self.students1[0])
        myMock.return_value = {'hljod': -1, 'mal': 15, 'bok': -1}
        ret = obj.calculated_results()
        myMock.assert_called_once_with()
        self.assertEqual(ret, expect)
        myMock.reset_mock()
        myMock.return_value = {'hljod': -1, 'mal': 16, 'bok': -1}
        ret = obj.calculated_results()
        myMock.assert_called_once_with()
        self.assertEqual(ret, expect)

    @mock.patch.object(SurveyResult, '_lesskimun_input_sums')
    def test_lesskimun_calculated_results_returns_ahaetta_2_for_8_to_10_in_bok(self, myMock):
        expect = ['Vantar gögn', 'Vantar gögn', 'Áhætta 2']
        obj = SurveyResult(survey=self.groupsurvey1, student=self.students1[0])
        myMock.return_value = {'hljod': -1, 'mal': -1, 'bok': 8}
        ret = obj.calculated_results()
        myMock.assert_called_once_with()
        self.assertEqual(ret, expect)
        myMock.reset_mock()
        myMock.return_value = {'hljod': -1, 'mal': -1, 'bok': 10}
        ret = obj.calculated_results()
        myMock.assert_called_once_with()
        self.assertEqual(ret, expect)

    @mock.patch.object(SurveyResult, '_lesskimun_input_sums')
    def test_lesskimun_calculated_results_returns_ovissa_for_18_to_19_in_hljod(self, myMock):
        expect = ['Óvissa', 'Vantar gögn', 'Vantar gögn']
        obj = SurveyResult(survey=self.groupsurvey1, student=self.students1[0])
        myMock.return_value = {'hljod': 18, 'mal': -1, 'bok': -1}
        ret = obj.calculated_results()
        myMock.assert_called_once_with()
        self.assertEqual(ret, expect)
        myMock.reset_mock()
        myMock.return_value = {'hljod': 19, 'mal': -1, 'bok': -1}
        ret = obj.calculated_results()
        myMock.assert_called_once_with()
        self.assertEqual(ret, expect)

    @mock.patch.object(SurveyResult, '_lesskimun_input_sums')
    def test_lesskimun_calculated_results_returns_ovissa_for_17_in_mal(self, myMock):
        expect = ['Vantar gögn', 'Óvissa', 'Vantar gögn']
        obj = SurveyResult(survey=self.groupsurvey1, student=self.students1[0])
        myMock.return_value = {'hljod': -1, 'mal': 17, 'bok': -1}
        ret = obj.calculated_results()
        myMock.assert_called_once_with()
        self.assertEqual(ret, expect)

    @mock.patch.object(SurveyResult, '_lesskimun_input_sums')
    def test_lesskimun_calculated_results_returns_ovissa_for_11_to_12_in_bok(self, myMock):
        expect = ['Vantar gögn', 'Vantar gögn', 'Óvissa']
        obj = SurveyResult(survey=self.groupsurvey1, student=self.students1[0])
        myMock.return_value = {'hljod': -1, 'mal': -1, 'bok': 11}
        ret = obj.calculated_results()
        myMock.assert_called_once_with()
        self.assertEqual(ret, expect)
        myMock.reset_mock()
        myMock.return_value = {'hljod': -1, 'mal': -1, 'bok': 12}
        ret = obj.calculated_results()
        myMock.assert_called_once_with()
        self.assertEqual(ret, expect)

    @mock.patch.object(SurveyResult, '_lesskimun_input_sums')
    def test_lesskimun_calculated_results_returns_utan_ahaettu_for_20_in_hljod(self, myMock):
        expect = ['Utan áhættu', 'Vantar gögn', 'Vantar gögn']
        obj = SurveyResult(survey=self.groupsurvey1, student=self.students1[0])
        myMock.return_value = {'hljod': 20, 'mal': -1, 'bok': -1}
        ret = obj.calculated_results()
        myMock.assert_called_once_with()
        self.assertEqual(ret, expect)

    @mock.patch.object(SurveyResult, '_lesskimun_input_sums')
    def test_lesskimun_calculated_results_returns_utan_ahaettu_for_18_in_mal(self, myMock):
        expect = ['Vantar gögn', 'Utan áhættu', 'Vantar gögn']
        obj = SurveyResult(survey=self.groupsurvey1, student=self.students1[0])
        myMock.return_value = {'hljod': -1, 'mal': 18, 'bok': -1}
        ret = obj.calculated_results()
        myMock.assert_called_once_with()
        self.assertEqual(ret, expect)

    @mock.patch.object(SurveyResult, '_lesskimun_input_sums')
    def test_lesskimun_calculated_results_returns_utan_ahaettu_for_13_in_bok(self, myMock):
        expect = ['Vantar gögn', 'Vantar gögn', 'Utan áhættu']
        obj = SurveyResult(survey=self.groupsurvey1, student=self.students1[0])
        myMock.return_value = {'hljod': -1, 'mal': -1, 'bok': 13}
        ret = obj.calculated_results()
        myMock.assert_called_once_with()
        self.assertEqual(ret, expect)
