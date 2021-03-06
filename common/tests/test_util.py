# -*- coding: utf-8 -*-
from django.test import TestCase, mock, RequestFactory
from django.core.urlresolvers import reverse
from django.core.exceptions import ObjectDoesNotExist


from ..models import (
    School,
)
import common.util

# Tests for common.util


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

    @mock.patch('common.util._is_school_manager')
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

    def test_get_studentgroup_id_returns_none_on_no_data(self):
        kwargs = {}
        mock_request = mock.Mock()
        mock_request.path = '/'
        ret = common.util.get_studentgroup_id(mock_request, kwargs)
        self.assertEqual(ret, None)

    def test_get_studentgroup_id_returns_contents_of_student_group_kwargs(self):
        kwargs = {'student_group': 1000}
        mock_request = mock.Mock()
        mock_request.path = '/'
        ret = common.util.get_studentgroup_id(mock_request, kwargs)
        self.assertEqual(ret, kwargs['student_group'])

    def test_get_studentgroup_id_returns_contents_of_studentgroup_id_kwargs(self):
        kwargs = {'studentgroup_id': 1000}
        mock_request = mock.Mock()
        mock_request.path = '/'
        ret = common.util.get_studentgroup_id(mock_request, kwargs)
        self.assertEqual(ret, kwargs['studentgroup_id'])

    @mock.patch('common.models.GroupSurvey')
    def test_get_studentgroup_id_returns_studentgroup_id_from_groupsurvey_if_kwargs_has_survey_id(self, myMockModel):
        myMockObj = mock.Mock()
        myMockObj.studentgroup.id = 1000
        myMockModel.objects.get.return_value = myMockObj
        mock_request = mock.Mock()
        mock_request.path = '/'
        kwargs = {'survey_id': 1001}
        ret = common.util.get_studentgroup_id(mock_request, kwargs)
        myMockModel.objects.get.assert_called_once_with(pk=1001)
        self.assertEqual(ret, 1000)

    @mock.patch('common.models.GroupSurvey')
    def test_get_studentgroup_id_rets_id_from_groupsurvey_if_kwargs_has_pk_and_path_has_prof(self, myMockModel):
        myMockObj = mock.Mock()
        myMockObj.studentgroup.id = 1000
        myMockModel.objects.get.return_value = myMockObj
        mock_request = mock.Mock()
        mock_request.path = '/próf'
        kwargs = {'pk': 1001}
        ret = common.util.get_studentgroup_id(mock_request, kwargs)
        myMockModel.objects.get.assert_called_once_with(pk=1001)
        self.assertEqual(ret, 1000)

    def test_get_studentgroup_id_rets_pk_if_kwargs_has_bekkur(self):
        kwargs = {'pk': 1000}
        mock_request = mock.Mock()
        mock_request.path = '/bekkur'
        ret = common.util.get_studentgroup_id(mock_request, kwargs)
        self.assertEqual(ret, kwargs['pk'])

    @mock.patch('common.models.StudentGroup')
    def test_get_studentgroup_id_returns_id_from_groupsurvey_if_path_has_nemandi_and_kwargs_has_pk(self, myMockModel):
        myMockObj = mock.Mock()
        myMockObj.id = 1000
        myMockFilter = mock.Mock()
        myMockFilter.first.return_value = myMockObj
        myMockModel.objects.filter.return_value = myMockFilter
        mock_request = mock.Mock()
        mock_request.path = '/nemandi'
        kwargs = {'pk': 1001}
        ret = common.util.get_studentgroup_id(mock_request, kwargs)
        myMockModel.objects.filter.assert_called_once_with(students=1001)
        self.assertEqual(ret, 1000)

    @mock.patch('common.models.GroupSurvey')
    def test_get_studentgroup_id_returns_none_if_filter_raises_objectdoesnotexist(self, myMockModel):
        myMockModel.objects.get.side_effect = ObjectDoesNotExist("I've excepted")
        mock_request = mock.Mock()
        mock_request.path = '/'
        kwargs = {'survey_id': 1001}
        ret = common.util.get_studentgroup_id(mock_request, kwargs)
        myMockModel.objects.get.assert_called_once_with(pk=1001)
        self.assertEqual(ret, None)

    def test_is_group_manager_returns_false_when_user_is_not_authenticated(self):
        mock_request = mock.Mock()
        mock_request.user.is_authenticated = False
        ret = common.util.is_group_manager(mock_request, {'pk': self.school_a.id})
        self.assertFalse(ret)

    def test_is_group_manager_returns_true_when_user_is_superuser(self):
        mock_request = mock.Mock()
        mock_request.user.is_authenticated = True
        mock_request.user.is_superuser = True
        ret = common.util.is_group_manager(mock_request, {'pk': self.school_a.id})
        self.assertTrue(ret)

    @mock.patch('common.util.get_studentgroup_id')
    def test_is_group_manager_returns_true_if_group_manager_asks(self, myMock):
        studentgroup = self.school_a.studentgroup_set.first()
        myMock.return_value = studentgroup.id
        user = studentgroup.group_managers.first().user
        request = self._generate_request(user)
        self.assertTrue(request.user.is_authenticated)
        kwargs = {'hello': 'world'}
        ret = common.util.is_group_manager(request, kwargs)
        myMock.assert_called_once_with(request, kwargs)
        self.assertTrue(ret)

    @mock.patch('common.util.get_studentgroup_id')
    def test_is_group_manager_returns_false_if_non_group_manager_asks(self, myMock):
        studentgroup = self.school_a.studentgroup_set.all()[0]
        otherstudentgroup = self.school_a.studentgroup_set.all()[1]
        myMock.return_value = studentgroup.id
        user = otherstudentgroup.group_managers.first().user
        request = self._generate_request(user)
        self.assertTrue(request.user.is_authenticated)
        kwargs = {'hello': 'world'}
        ret = common.util.is_group_manager(request, kwargs)
        myMock.assert_called_once_with(request, kwargs)
        self.assertFalse(ret)

    def test_get_groupsurvey_id_returns_groupsurvey_id_if_in_kwargs(self):
        kwargs = {'groupsurvey_id': 1000}
        ret = common.util.get_groupsurvey_id(kwargs)
        self.assertEqual(ret, kwargs['groupsurvey_id'])

    def test_get_groupsurvey_id_returns_survey_id_if_in_kwargs(self):
        kwargs = {'survey_id': 1000}
        ret = common.util.get_groupsurvey_id(kwargs)
        self.assertEqual(ret, kwargs['survey_id'])

    def test_get_groupsurvey_id_returns_pk_if_in_kwargs(self):
        kwargs = {'pk': 1000}
        ret = common.util.get_groupsurvey_id(kwargs)
        self.assertEqual(ret, kwargs['pk'])

    def test_groupsurvey_is_open_returns_false_when_user_is_not_authenticated(self):
        mock_request = mock.Mock()
        mock_request.user.is_authenticated = False
        ret = common.util.groupsurvey_is_open(mock_request, {'pk': 1})
        self.assertFalse(ret)

    def test_groupsurvey_is_open_returns_true_when_user_is_superuser(self):
        mock_request = mock.Mock()
        mock_request.user.is_authenticated = True
        mock_request.user.is_superuser = True
        ret = common.util.groupsurvey_is_open(mock_request, {'pk': 1})
        self.assertTrue(ret)

    @mock.patch('common.util.get_groupsurvey_id')
    def test_groupsurvey_is_open_returns_false_if_get_groupsurvey_id_returns_none(self, myMock):
        mock_request = mock.Mock()
        mock_request.user.is_authenticated = True
        mock_request.user.is_superuser = False

        myMock.return_value = None
        kwargs = {'pk': 1000}
        ret = common.util.groupsurvey_is_open(mock_request, kwargs)
        myMock.assert_called_once_with(kwargs)
        self.assertFalse(ret)

    @mock.patch('common.util.get_groupsurvey_id')
    @mock.patch('common.models.GroupSurvey')
    def test_groupsurvey_is_open_returns_true_for_open_groupsurvey(self, myMockModel, myMockFunction):
        myMockObj2 = mock.Mock()
        myMockObj2.is_open.return_value = True
        myMockObj1 = mock.Mock()
        myMockObj1.first.return_value = myMockObj2
        myMockModel.objects.filter.return_value = myMockObj1
        myMockFunction.return_value = 1000
        mock_request = mock.Mock()
        mock_request.user.is_authenticated = True
        mock_request.user.is_superuser = False
        kwargs = {'hello': 'world'}

        ret = common.util.groupsurvey_is_open(mock_request, kwargs)
        myMockFunction.assert_called_once_with(kwargs)
        myMockModel.objects.filter.assert_called_once_with(pk=1000)
        myMockObj1.first.assert_called_once_with()
        myMockObj2.is_open.assert_called_once_with()
        self.assertTrue(ret)

    def test_slug_sort_sorts(self):
        class TestObj(object):
            def __init__(self, value):
                self.name = value

            def __str__(self):
                return self.name

        TestObj1 = TestObj('Aye')
        TestObj2 = TestObj('Bee')
        TestObj3 = TestObj('Cee')

        input_list = [TestObj2, TestObj3, TestObj1]
        expected_output = [TestObj1, TestObj2, TestObj3]

        ret = common.util.slug_sort(input_list, 'name')
        self.assertEqual(ret, expected_output)

    def test_add_field_classes(self):
        myObj = mock.Mock()
        myObj.fields = {'hello': mock.Mock(), 'world': mock.Mock(), 'again': mock.Mock()}
        cssdef = {'test': 'testing'}
        ret = common.util.add_field_classes(myObj, ['hello', 'world'], cssdef)
        self.assertEqual(ret, None)
        myObj.fields['hello'].widget.attrs.update.assert_called_once_with(cssdef)
        myObj.fields['world'].widget.attrs.update.assert_called_once_with(cssdef)
        myObj.fields['again'].widget.attrs.update.assert_not_called()


class ImportDataUtilTests(TestCase):
    slug = 'my_test'
    fake_data = [{'hello': 'world'}, {'this': 'is'}, {'a': 'test'}, {'error': 'is here'}]
    expected_data = [{'hello': 'world'}, {'this': 'is'}, {'a': 'test'}, {}]

    def setUp(self):
        class FakeRequestWithSession:
            session = {}
        self.fake_request = FakeRequestWithSession()

    def _step1(self):
        self.cache_id = common.util.store_import_data(self.fake_request, self.slug, self.fake_data)

    def _step2(self):
        return common.util.get_import_data(self.fake_request, self.slug)

    def _step3(self):
        common.util.cancel_import_data(self.fake_request, self.slug)

    def _run_step1(self):
        self._step1()
        self.assertTrue(self.slug in self.fake_request.session)
        self.assertEqual(self.fake_request.session[self.slug], self.cache_id)
        self.myMock.set.assert_called_once_with(self.cache_id, self.expected_data, 15 * 60)
        self.myMock.reset_mock()

    def _run_step2(self):
        self.myMock.get.return_value = self.expected_data
        data = self._step2()
        self.assertFalse(self.slug in self.fake_request.session)
        self.assertEqual(self.expected_data, data)
        self.myMock.get.assert_called_once_with(self.cache_id)
        self.myMock.delete.assert_called_once_with(self.cache_id)
        self.myMock.reset_mock()

    def _run_step3(self):
        self._step3()
        self.assertFalse(self.slug in self.fake_request.session)
        self.myMock.delete.assert_called_once_with(self.cache_id)
        self.myMock.reset_mock()

    @mock.patch('common.util.cache')
    def test_import_data_functions(self, myMock):
        self.myMock = myMock
        self._run_step1()
        self._run_step2()
        self._run_step1()
        self._run_step3()
