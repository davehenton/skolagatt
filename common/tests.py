# -*- coding: utf-8 -*-
from django.test import TestCase, mock, RequestFactory
from django.core.urlresolvers import reverse

from .models import (
    School,
    GroupSurvey,
    SurveyResult,
)
from .forms import (
    SchoolForm,
    StudentForm,
)
from survey.models import (
    Survey,
    SurveyType,
    SurveyTransformation,
)
import common.util


class UtilTests(TestCase):
    fixtures = ['auth', 'common']

    def setUp(self):
        super(UtilTests, self).setUp()
        self.factory = RequestFactory()
        self.school_a = School.objects.all()[0]
        self.school_b = School.objects.all()[1]

    def _generate_request(self, user):
        request = self.factory.get(reverse('index'))
        request.user = user
        return request

    def test_util_get_current_school_returns_school_id(self):
        kwargs = {'school_id': 1000}
        ret = common.util.get_current_school(kwargs)
        self.assertEqual(ret, 1000)

    def test_util_get_current_school_returns_pk(self):
        kwargs = {'pk': 1000}
        ret = common.util.get_current_school(kwargs)
        self.assertEqual(ret, 1000)

    def test_util_get_current_school_prefers_school_id_over_pk(self):
        kwargs = {'school_id': 1000, 'pk': 1001}
        ret = common.util.get_current_school(kwargs)
        self.assertEqual(ret, 1000)

    def test_util_get_current_studentgroup_returns_studentgroup_id(self):
        kwargs = {'studentgroup_id': 1000}
        ret = common.util.get_current_studentgroup(kwargs)
        self.assertEqual(ret, 1000)

    def test_util_get_current_studentgroup_returns_pk(self):
        kwargs = {'pk': 1000}
        ret = common.util.get_current_studentgroup(kwargs)
        self.assertEqual(ret, 1000)

    def test_util_get_current_studentgroup_prefers_studentgroup_id_over_pk(self):
        kwargs = {'studentgroup_id': 1000, 'pk': 1001}
        ret = common.util.get_current_studentgroup(kwargs)
        self.assertEqual(ret, 1000)

    def test_util_get_current_school_returns_none_without_school_id_or_pk(self):
        kwargs = {'thing': 1000}
        ret = common.util.get_current_school(kwargs)
        self.assertEqual(ret, None)

    def test_is_school_manager_returns_true_for_superuser(self):
        mock_request = mock.Mock()
        mock_request.user.is_superuser = True
        ret = common.util.is_school_manager(mock_request, {})
        self.assertTrue(ret)

    def test_is_school_manager_returns_false_if_not_logged_in(self):
        mock_request = mock.Mock()
        mock_request.user.is_authenticated = False
        ret = common.util.is_school_manager(mock_request, {})
        self.assertFalse(ret)

    def test_is_school_manager_returns_true_if_logged_in_as_manager(self):
        user = self.school_a.managers.first().user
        request = self._generate_request(user)
        self.assertTrue(request.user.is_authenticated)
        ret = common.util.is_school_manager(request, {'pk': self.school_a.id})
        self.assertTrue(ret)

    def test_is_school_manager_returns_false_if_logged_in_as_teacher(self):
        user = self.school_a.teachers.first().user
        request = self._generate_request(user)
        self.assertTrue(request.user.is_authenticated)
        ret = common.util.is_school_manager(request, {'pk': self.school_a.id})
        self.assertFalse(ret)

    def test_is_school_manager_returns_false_if_logged_in_as_manager_for_another_school(self):
        user = self.school_a.managers.first().user
        request = self._generate_request(user)
        self.assertTrue(request.user.is_authenticated)
        ret = common.util.is_school_manager(request, {'pk': self.school_b.id})
        self.assertFalse(ret)

    @mock.patch('common.util.get_current_school')
    def test_is_school_manager_returns_false_on_exception(self, myMock):
        myMock.side_effect = Exception("I've excepted")
        user = self.school_a.managers.first().user
        request = self._generate_request(user)
        self.assertTrue(request.user.is_authenticated)
        kwargs = {'pk': self.school_a.id}
        ret = common.util.is_school_manager(request, kwargs)
        myMock.assert_called_once_with(kwargs)
        self.assertFalse(ret)

    def test_is_manager_returns_false_when_user_is_unauthenticated(self):
        mock_request = mock.Mock()
        mock_request.user.is_authenticated = False
        ret = common.util.is_manager(mock_request)
        self.assertFalse(ret)

    def test_is_manager_returns_false_when_user_is_not_manager(self):
        user = self.school_a.teachers.first().user
        request = self._generate_request(user)
        self.assertTrue(request.user.is_authenticated)
        ret = common.util.is_manager(request)
        self.assertFalse(ret)

    def test_is_manager_returns_true_when_user_is_manager(self):
        user = self.school_a.managers.first().user
        request = self._generate_request(user)
        self.assertTrue(request.user.is_authenticated)
        ret = common.util.is_manager(request)
        self.assertTrue(ret)

    def test_is_school_teacher_returns_false_when_user_is_not_authenticated(self):
        mock_request = mock.Mock()
        mock_request.user.is_authenticated = False
        ret = common.util.is_school_teacher(mock_request, {'pk': self.school_a.id})
        self.assertFalse(ret)

    def test_is_school_teacher_returns_true_when_user_is_superuser(self):
        mock_request = mock.Mock()
        mock_request.user.is_authenticated = True
        mock_request.user.is_superuser = True
        ret = common.util.is_school_teacher(mock_request, {'pk': self.school_a.id})
        self.assertTrue(ret)

    @mock.patch('common.util.is_school_manager')
    def test_is_school_teacher_calls_is_school_manager_and_returns_true_if_true(self, myMock):
        myMock.return_value = True
        mock_request = mock.Mock()
        mock_request.user.is_authenticated = True
        mock_request.user.is_superuser = False
        kwargs = {'pk': 1000}
        ret = common.util.is_school_teacher(mock_request, kwargs)
        myMock.assert_called_once_with(mock_request, kwargs)
        self.assertTrue(ret)

    def test_is_school_teacher_returns_true_if_it_gets_a_real_school_teacher(self):
        teacher = self.school_a.teachers.first()
        user = teacher.user
        request = self._generate_request(user)
        kwargs = {'school_id': self.school_a.id, 'pk': teacher.studentgroup_set.first().id}
        self.assertTrue(request.user.is_authenticated)
        ret = common.util.is_school_teacher(request, kwargs)
        self.assertTrue(ret)

    def test_is_school_teacher_returns_false_if_it_gets_a_teacher_from_another_school(self):
        teacher = self.school_b.teachers.first()
        user = teacher.user
        request = self._generate_request(user)
        kwargs = {'school_id': self.school_a.id, 'pk': teacher.studentgroup_set.first().id}
        self.assertTrue(request.user.is_authenticated)
        ret = common.util.is_school_teacher(request, kwargs)
        self.assertFalse(ret)

    def test_is_school_teacher_returns_false_if_it_gets_a_teacher_from_same_school_but_another_group(self):
        teacher = self.school_a.teachers.all()[1]
        otherstudentgroup = self.school_a.teachers.all()[0].studentgroup_set.first()
        user = teacher.user
        request = self._generate_request(user)
        kwargs = {'school_id': self.school_a.id, 'pk': otherstudentgroup.id}
        self.assertTrue(request.user.is_authenticated)
        ret = common.util.is_school_teacher(request, kwargs)
        self.assertFalse(ret)

    def test_is_teacher_returns_false_when_user_is_not_authenticated(self):
        mock_request = mock.Mock()
        mock_request.user.is_authenticated = False
        ret = common.util.is_teacher(mock_request)
        self.assertFalse(ret)

    def test_is_teacher_returns_true_when_user_is_teacher(self):
        teacher = self.school_a.teachers.first()
        user = teacher.user
        request = self._generate_request(user)
        self.assertTrue(request.user.is_authenticated)
        ret = common.util.is_teacher(request)
        self.assertTrue(ret)

    def test_is_teacher_returns_false_when_user_is_not_teacher(self):
        manager = self.school_a.managers.first()
        user = manager.user
        request = self._generate_request(user)
        self.assertTrue(request.user.is_authenticated)
        ret = common.util.is_teacher(request)
        self.assertFalse(ret)



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


class FormWithSsnFieldTests(TestCase):
    def setUp(self):
        super(FormWithSsnFieldTests, self).setUp()
        self.school_testdict = {
            'name': 'Formlegi skólinn',
            'ssn': '5708150320',
            'managers': [],
            'teachers': [],
            'school_nr': 5555,
            'address': 'Víkurhvarfi 3',
            'post_code': '203',
            'municipality': 'Kópavogsbær',
            'part': 'Ngr. Reykjavíkur',
        }
        self.student_testdict = {
            'ssn': '0101005930',
            'name': 'Barn Föðurz'
        }

    def test_valid_school_form(self):
        form = SchoolForm(self.school_testdict)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.errors, {})
        school = form.save()
        self.assertEqual(school.name, self.school_testdict['name'])
        self.assertEqual(school.ssn, self.school_testdict['ssn'])
        self.assertEqual(school.managers.count(), len(self.school_testdict['managers']))
        self.assertEqual(school.teachers.count(), len(self.school_testdict['teachers']))
        self.assertEqual(school.school_nr, self.school_testdict['school_nr'])
        self.assertEqual(school.address, self.school_testdict['address'])
        self.assertEqual(school.post_code, self.school_testdict['post_code'])
        self.assertEqual(school.municipality, self.school_testdict['municipality'])
        self.assertEqual(school.part, self.school_testdict['part'])

    def test_school_form_invalid_ssn_reports_error(self):
        testdict = self.school_testdict.copy()
        testdict['ssn'] = '1111'
        form = SchoolForm(testdict)
        self.assertFalse(form.is_valid())
        self.assertTrue('ssn' in form.errors)
        self.assertEqual(form.errors['ssn'], ['Kennitala ekki rétt slegin inn'])

    def test_school_form_personal_ssn_reports_error(self):
        testdict = self.school_testdict.copy()
        testdict['ssn'] = self.student_testdict['ssn']
        form = SchoolForm(testdict)
        self.assertFalse(form.is_valid())
        self.assertTrue('ssn' in form.errors)
        self.assertEqual(form.errors['ssn'], ['Kennitala ekki rétt slegin inn'])

    def test_valid_student_form(self):
        form = StudentForm(self.student_testdict)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.errors, {})
        student = form.save()
        self.assertEqual(student.name, self.student_testdict['name'])
        self.assertEqual(student.ssn, self.student_testdict['ssn'])

    def test_student_form_invalid_ssn_reports_error(self):
        testdict = self.student_testdict.copy()
        testdict['ssn'] = '1111'
        form = StudentForm(testdict)
        self.assertFalse(form.is_valid())
        self.assertTrue('ssn' in form.errors)
        self.assertEqual(form.errors['ssn'], ['Kennitala ekki rétt slegin inn'])

    def test_student_form_business_ssn_reports_error(self):
        testdict = self.student_testdict.copy()
        testdict['ssn'] = self.school_testdict['ssn']
        form = StudentForm(testdict)
        self.assertFalse(form.is_valid())
        self.assertTrue('ssn' in form.errors)
        self.assertEqual(form.errors['ssn'], ['Kennitala ekki rétt slegin inn'])
