# -*- coding: utf-8 -*-
from django.test import TestCase, Client, RequestFactory, mock
from django.utils import timezone
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

from common.models import (
    School,
    Teacher,
    Manager,
)
from ..views import (
    SchoolListing,
    SchoolDetail,
    SchoolCreate,
    SchoolUpdate,
)
from skolagatt.test_utils import kennitala_get, instance_to_dict
from common.util import slug_sort

# Tests for schools.views


class SchoolListingViewTests(TestCase):
    fixtures = ['auth', 'common']

    def setUp(self):
        super(SchoolListingViewTests, self).setUp()
        self.client = Client()
        self.factory = RequestFactory()

    def test_school_list_without_login_lists_nothing(self):
        response = self.client.get(reverse('schools:school_listing'))
        self.assertEqual(response.status_code, 200)
        self.assertNotIn('school_list', response.context)
        self.assertContains(response, 'Vinsamlegast skráðu þig inn.')

    def test_school_list_shows_all_schools_to_superuser(self):
        user = User.objects.filter(is_superuser=True).first()
        request = self.factory.get(reverse('schools:school_listing'))
        request.user = user
        response = SchoolListing.as_view()(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context_data['school_list']), 2)
        self.assertContains(response, 'Akureyrarskólinn')
        self.assertContains(response, 'Höfuðborgarskólinn')

    def test_school_list_redirects_to_school_detail_for_manager(self):
        school = School.objects.get(name='Höfuðborgarskólinn')
        request = self.factory.get(reverse('schools:school_listing'))
        request.user = school.managers.first().user  # We appear logged in as the manager of 'Höfuðborgarskólinn'
        response = SchoolListing.as_view()(request)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('schools:school_detail', kwargs={'pk': school.id}))

    def test_school_list_redirects_to_group_detail_for_teacher(self):
        school = School.objects.get(name='Akureyrarskólinn')
        studentgroup = school.studentgroup_set.filter(name='4. bekkur').first()
        request = self.factory.get(reverse('schools:school_listing'))
        request.user = studentgroup.group_managers.first().user
        response = SchoolListing.as_view()(request)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('schools:group_detail', kwargs={
            'school_id': school.id,
            'pk': studentgroup.id
        }))

    def test_school_list_redirects_to_school_detail_for_teacher_that_has_multiple_groups(self):
        school = School.objects.get(name='Höfuðborgarskólinn')
        group2 = school.studentgroup_set.filter(name='2. bekkur').first()
        group3 = school.studentgroup_set.filter(name='3. bekkur').first()
        ssn = kennitala_get(1995)
        new_user = User.objects.create(
            username=ssn,
            date_joined=timezone.now(),
            last_login=timezone.now(),
        )
        new_teacher = Teacher.objects.create(
            ssn=ssn,
            name='Nýr Kennari',
            user=new_user,
        )
        group2.group_managers.add(new_teacher)
        group2.save()
        group3.group_managers.add(new_teacher)
        group3.save()
        school.teachers.add(new_teacher)
        request = self.factory.get(reverse('schools:school_listing'))
        request.user = new_user
        response = SchoolListing.as_view()(request)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('schools:school_detail', kwargs={'pk': school.id}))

    def test_school_list_teacher_not_in_any_school_gets_empty_list(self):
        ssn = kennitala_get(1995)
        new_user = User.objects.create(
            username=ssn,
            date_joined=timezone.now(),
            last_login=timezone.now(),
        )
        Teacher.objects.create(
            ssn=ssn,
            name='Nýr Kennari',
            user=new_user,
        )
        request = self.factory.get(reverse('schools:school_listing'))
        request.user = new_user
        response = SchoolListing.as_view()(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context_data['school_list']), 0)
        self.assertNotContains(response, 'Akureyrarskólinn')
        self.assertNotContains(response, 'Höfuðborgarskólinn')

    def test_school_list_shows_relevant_schools_to_managers_that_manage_multiple_schools(self):
        ssn = kennitala_get(1995)
        new_user = User.objects.create(
            username=ssn,
            date_joined=timezone.now(),
            last_login=timezone.now(),
        )
        new_manager = Manager.objects.create(
            ssn=ssn,
            name='Nýr Kennari',
            user=new_user,
        )
        new_school = School.objects.create(
            name='Nýi skólinn',
            ssn=kennitala_get(2017),
        )
        new_school.managers.add(new_manager)
        new_school.save()
        old_school = School.objects.get(name='Akureyrarskólinn')
        old_school.managers.add(new_manager)
        old_school.save()
        request = self.factory.get(reverse('schools:school_listing'))
        request.user = new_user
        response = SchoolListing.as_view()(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context_data['school_list']), 2)
        self.assertContains(response, new_school.name)
        self.assertContains(response, old_school.name)
        self.assertNotContains(response, 'Höfuðborgarskólinn')

    def test_school_list_manager_without_any_school_gets_empty_list(self):
        ssn = kennitala_get(1995)
        new_user = User.objects.create(
            username=ssn,
            date_joined=timezone.now(),
            last_login=timezone.now(),
        )
        Manager.objects.create(
            ssn=ssn,
            name='Nýr Skólastjóri',
            user=new_user,
        )
        request = self.factory.get(reverse('schools:school_listing'))
        request.user = new_user
        response = SchoolListing.as_view()(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context_data['school_list']), 0)
        self.assertNotContains(response, 'Akureyrarskólinn')
        self.assertNotContains(response, 'Höfuðborgarskólinn')


class SchoolDetailViewTests(TestCase):
    fixtures = ['auth', 'common']

    def setUp(self):
        super(SchoolDetailViewTests, self).setUp()
        self.client = Client()
        self.factory = RequestFactory()
        self.school = School.objects.get(name='Akureyrarskólinn')

    def _call_school_detail_view(self, user):
        kwargs = {'pk': self.school.id}
        request = self.factory.get(reverse('schools:school_detail', kwargs=kwargs))
        request.user = user
        return SchoolDetail.as_view()(request, **kwargs)

    def _check_school_detail_view_output(self, response):
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.school.name)
        self.assertEqual(len(response.context_data['studentgroup_list']), self.school.studentgroup_set.count())
        self.assertEqual(len(response.context_data['managers']), self.school.managers.count())
        self.assertEqual(len(response.context_data['teachers']), self.school.teachers.count())
        self.assertEqual(len(response.context_data['students']), self.school.students.count())

        self.assertEqual(slug_sort(response.context_data['studentgroup_list'], 'name'), slug_sort(
            self.school.studentgroup_set.all(), 'name'))
        self.assertEqual(slug_sort(response.context_data['managers'], 'name'), slug_sort(
            self.school.managers.all(), 'name'))
        self.assertEqual(slug_sort(response.context_data['teachers'], 'name'), slug_sort(
            self.school.teachers.all(), 'name'))
        self.assertEqual(slug_sort(response.context_data['students'], 'name'), slug_sort(
            self.school.students.all(), 'name'))

    def test_school_detail_without_login_gets_denied(self):
        response = self.client.get(reverse('schools:school_detail', kwargs={'pk': self.school.id}))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/denied'))

    def test_school_detail_shows_all_data_for_school_manager(self):
        user = self.school.managers.first().user
        response = self._call_school_detail_view(user)
        self._check_school_detail_view_output(response)

    def test_school_detail_shows_all_data_for_school_teacher(self):
        user = self.school.teachers.first().user
        response = self._call_school_detail_view(user)
        self._check_school_detail_view_output(response)

    def test_school_detail_denies_access_to_nonrelevant_managers(self):
        otherschool = School.objects.get(name='Höfuðborgarskólinn')
        user = otherschool.managers.first().user
        response = self._call_school_detail_view(user)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/denied'))


class SchoolCreateViewTests(TestCase):
    fixtures = ['auth', 'common']

    def setUp(self):
        super(SchoolCreateViewTests, self).setUp()
        self.client = Client()
        self.factory = RequestFactory()

    def test_school_create_view(self):
        user = User.objects.filter(is_superuser=True).first()
        data = {
            'name': 'Nýi skólinn',
            'ssn': '5708150320',
        }
        self.assertEqual(School.objects.count(), 2)
        request = self.factory.post(reverse('schools:school_create'), data)
        request.user = user
        response = SchoolCreate.as_view()(request, {})

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('schools:school_listing'))
        self.assertEqual(School.objects.count(), 3)
        newschool = School.objects.last()
        self.assertEqual(newschool.name, data['name'])
        self.assertEqual(newschool.ssn, data['ssn'])

    def test_school_create_view_fails_for_non_superuser(self):
        user = User.objects.filter(is_superuser=False).first()
        data = {
            'name': 'Nýi skólinn',
            'ssn': '5708150320',

        }
        self.assertEqual(School.objects.count(), 2)
        request = self.factory.post(reverse('schools:school_create'), data)
        request.user = user
        response = SchoolCreate.as_view()(request, {})
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/denied'))
        self.assertEqual(School.objects.count(), 2)


class SchoolUpdateViewTests(TestCase):
    fixtures = ['auth', 'common']

    def setUp(self):
        super(SchoolUpdateViewTests, self).setUp()
        self.client = Client()
        self.factory = RequestFactory()
        self.school = School.objects.get(name='Akureyrarskólinn')
        self.super_user = User.objects.filter(is_superuser=True).first()
        self.client.login(username=self.super_user.username, password=self.super_user.password)
        self.data = instance_to_dict(self.school)

    @mock.patch('common.forms.FormWithSsnField._validate_ssn')
    def _test_school_update_view_change_field(self, field, value, myMock):
        myMock.return_value = True
        update_data = instance_to_dict(self.school)
        update_data[field] = value

        self.assertEqual(School.objects.count(), 2)

        url = reverse('schools:school_update', kwargs={'pk': self.school.id})
        request = self.factory.post(url, update_data)
        request.user = self.super_user
        response = SchoolUpdate.as_view()(request, pk=self.school.id)
        myMock.assert_called_once_with('ssn')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('schools:school_listing'))
        self.assertEqual(School.objects.count(), 2)

        updated_school = School.objects.get(pk=self.school.id)
        updated_data = instance_to_dict(updated_school)
        self.assertTrue(updated_data[field] == value)
        self.assertTrue(update_data == updated_data)

    def test_school_update_view_change_name(self):
        self._test_school_update_view_change_field('name', 'Þorpsskólinn')

    def test_school_update_view_change_ssn(self):
        self._test_school_update_view_change_field('ssn', kennitala_get(1980))

    def test_school_update_view_change_post_code(self):
        self._test_school_update_view_change_field('post_code', '602')

    def test_school_update_view_change_address(self):
        self._test_school_update_view_change_field('address', 'Bjarkarstígur 121')

    def test_school_update_view_change_municipality(self):
        self._test_school_update_view_change_field('municipality', 'Reykjavíkurborg')

    def test_school_update_view_change_part(self):
        self._test_school_update_view_change_field('part', 'Reykjavík')

    def test_school_update_view_change_school_nr(self):
        self._test_school_update_view_change_field('school_nr', 6666)
