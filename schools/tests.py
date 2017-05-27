# -*- coding: utf-8 -*-
from django.test import TestCase, Client, RequestFactory
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

from common.models import (
    School,
)
from .views import (
    SchoolListing,
)


class SchoolListingViewTests(TestCase):
    fixtures = ['auth', 'common']

    def setUp(self):
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
        # import pdb; pdb.set_trace()
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
