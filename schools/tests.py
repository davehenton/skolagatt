# -*- coding: utf-8 -*-
from django.test import TestCase, Client, RequestFactory
from django.utils import timezone
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

from common.models import (
    School,
    Teacher,
    Manager,
)
from .views import (
    SchoolListing,
    SchoolDetail,
)
from skolagatt.test_utils import kennitala_get
from common.util import slug_sort


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
