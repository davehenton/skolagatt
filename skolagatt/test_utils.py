# -*- coding: utf-8 -*-
from django.utils import timezone
from django.forms.models import model_to_dict

from lxml import html
import requests
import random
from kennitala import Kennitala
import datetime

from common.models import (
    Student,
    StudentGroup,
    School,
    User,
    Teacher,
    Manager,
)


def kennitala_get(year):
    start_date = datetime.date(year, 1, 1).toordinal()
    end_date = datetime.date(year, 12, 31).toordinal()
    random_date = datetime.date.fromordinal(random.randint(start_date, end_date))
    kt = Kennitala('')
    return kt.generate(random_date)


def instance_to_dict(instance):
    return model_to_dict(instance, fields=[field.name for field in instance._meta.fields])


class FixtureGenerator(object):
    def __init__(self):
        self.kk_page = requests.get('https://is.wikipedia.org/wiki/Listi_yfir_íslensk_eiginnöfn_karlmanna')
        self.kvk_page = requests.get('https://is.wikipedia.org/wiki/Listi_yfir_%C3%ADslensk_eiginn%C3%B6fn_kvenmanna')

        self.kk_tree = html.fromstring(self.kk_page.content)
        self.kvk_tree = html.fromstring(self.kvk_page.content)

        self.kk_nofn = self.kk_tree.xpath('//div[@id="mw-content-text"]/ul/li/a/text()')[0:-2]
        self.kvk_nofn = self.kvk_tree.xpath('//div[@id="mw-content-text"]/ul/li/a/text()')[0:-2]

        self.nofn = []
        self.nofn.append(self.kk_nofn)
        self.nofn.append(self.kvk_nofn)

        self.KYN_KK = 0
        self.KYN_KVK = 1

        self.student_years = [
            (1, 2010),
            (2, 2009),
            (3, 2008),
            (4, 2007),
            (5, 2006),
            (6, 2005),
            (7, 2004),
            (8, 2003),
            (9, 2002),
            (10, 2001),
        ]

    def fodurnafn_get(self, kyn):
        fodurnafn_url = 'https://is.wikipedia.org'
        fodurnafn_fj = len(self.nofn[0])
        fodurnafn_i = random.randint(0, fodurnafn_fj - 1)
        nafn = self.nofn[0][fodurnafn_i]
        url_search = '//div[@id="mw-content-text"]/ul/li/a[@title="{}"]/@href'.format(nafn)
        fodurnafn = self.kk_tree.xpath(url_search)
        if len(fodurnafn) > 0:
            fodurnafn_url += fodurnafn[0]
            fodurnafn_page = requests.get(fodurnafn_url)
            fodurnafn_tree = html.fromstring(fodurnafn_page.content)
            trs = fodurnafn_tree.xpath('//table/tr')
            for tr in trs:
                tds = tr.getchildren()
                if tds[0].text_content() == 'Eignarfall':
                    ef_nafn = tds[1].text_content().split(' ')
                    output = ef_nafn[0]
                    if kyn == self.KYN_KVK:
                        output += 'dóttir'
                    elif kyn == self.KYN_KK:
                        output += 'son'
                    return output
        return self.fodurnafn_get(kyn)

    def get_name(self):
        output = ''
        kyn = random.randint(0, 1)
        nafn_fj = len(self.nofn[kyn])
        nafn = random.randint(0, nafn_fj - 1)
        output += self.nofn[kyn][nafn]
        # Athuga hvort við ætlum að hafa miðnafn
        if random.randint(0, 2) in [0, 1]:
            output += ' '
            midnafn = random.randint(0, nafn_fj - 1)
            output += self.nofn[kyn][midnafn]
        output += ' '
        output += self.fodurnafn_get(kyn)
        return output

    def generate_students(self):
        if Student.objects.count() > 0:
            return  # Avoid adding students to populated database

        for school in School.objects.all():
            for student_year, year in self.student_years:
                studentgroup = StudentGroup.objects.get(school=school, student_year=student_year)
                for i in range(0, 20):
                    kennitala = kennitala_get(year)
                    name = self.get_name()
                    student = Student.objects.create(name=name, ssn=kennitala)
                    school.students.add(student)
                    studentgroup.students.add(student)

    def generate_teachers(self):
        if Teacher.objects.count() > 0:
            return  # Avoid adding teachers to populated database

        for school in School.objects.all():
            for studentgroup in StudentGroup.objects.filter(school=school).all():
                year = random.randint(1947, 1997)
                kennitala = kennitala_get(year)
                name = self.get_name()
                user = User.objects.create(username=kennitala, date_joined=timezone.now(), last_login=timezone.now())
                teacher = Teacher.objects.create(ssn=kennitala, name=name, user=user)
                school.teachers.add(teacher)
                studentgroup.group_managers.add(teacher)

    def generate_managers(self):
        if Manager.objects.count() > 0:
            return  # Avoid adding managers to populated database

        for school in School.objects.all():
            year = random.randint(1957, 1987)
            kennitala = kennitala_get(year)
            name = self.get_name()
            user = User.objects.create(username=kennitala, date_joined=timezone.now(), last_login=timezone.now())
            manager = Manager.objects.create(ssn=kennitala, name=name, user=user)
            school.managers.add(manager)
