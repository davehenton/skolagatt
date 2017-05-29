# -*- coding: utf-8 -*-
from django.test import TestCase
from ..forms import (
    SchoolForm,
    StudentForm,
)

# Tests for common.forms


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
