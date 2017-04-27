# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

from django.contrib.auth.models import User
from django.utils import timezone

import json

from froala_editor.fields import FroalaField

from survey.models import Survey


class Notification(models.Model):
    notification_type = models.CharField(max_length=128)
    notification_id = models.IntegerField()
    user = models.ForeignKey(User)

    class Meta:
        unique_together = (("notification_type", "notification_id"),)

    def __str__(self):
        return self.notification_type


class Manager(models.Model):
    ssn = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=128)
    email = models.CharField(max_length=256, blank=True)
    phone = models.CharField(max_length=7, blank=True)
    position = models.CharField(max_length=256, blank=True)
    user = models.ForeignKey(User)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Teacher(models.Model):
    ssn = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=128)
    position = models.CharField(max_length=256, blank=True)
    user = models.ForeignKey(User)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Student(models.Model):
    # Although Icelandic kt are all just 10 characters, some schools have students that
    # don't seem to have icelandic kt's. Hence, the 32 char max_length for ssn
    ssn = models.CharField(max_length=32, unique=True)
    name = models.CharField(max_length=128)

    def get_distinct_surveys(self):
        groups = self.studentgroup_set.all().values_list('groupsurvey__pk', flat=True)
        surveys = GroupSurvey.objects.filter(pk__in=[x for x in groups if x is not None]).distinct()
        return surveys

    def get_distinct_survey_results(self):
        return self.surveyresult_set.all()

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class School(models.Model):
    MUNICIPALITIES = (
        ('Hafnarfjarðarkaupstaður', 'Hafnarfjarðarkaupstaður'),
        ('Reykjanesbær', 'Reykjanesbær'),
        ('Garðabær', 'Garðabær'),
        ('Dalabyggð', 'Dalabyggð'),
        ('Reykjavíkurborg', 'Reykjavíkurborg'),
        ('Kópavogsbær', 'Kópavogsbær'),
        ('Dalvíkurbyggð', 'Dalvíkurbyggð'),
        ('Sveitarf. Skagafjörður', 'Sveitarf. Skagafjörður'),
        ('Sveitarfélagið Árborg', 'Sveitarfélagið Árborg'),
        ('Bláskógabyggð', 'Bláskógabyggð'),
        ('Blönduósbær', 'Blönduósbær'),
        ('Norðurþing', 'Norðurþing'),
        ('Akraneskaupstaður', 'Akraneskaupstaður'),
        ('Akureyrarkaupstaður', 'Akureyrarkaupstaður'),
        ('Fljótsdalshérað', 'Fljótsdalshérað'),
        ('Árneshreppur', 'Árneshreppur'),
        ('Flóahreppi', 'Flóahreppi'),
        ('Hrunamannahreppur', 'Hrunamannahreppur'),
        ('Sveitarfélagið Garður', 'Sveitarfélagið Garður'),
        ('Grýtubakkahreppur', 'Grýtubakkahreppur'),
        ('Bolungarvíkurkaupstaður', 'Bolungarvíkurkaupstaður'),
        ('Borgarbyggð', 'Borgarbyggð'),
        ('Borgarfjarðarhreppur', 'Borgarfjarðarhreppur'),
        ('Djúpavogshreppur', 'Djúpavogshreppur'),
        ('Fjarðabyggð', 'Fjarðabyggð'),
        ('Fjallabyggð', 'Fjallabyggð'),
        ('Grindavíkurbær', 'Grindavíkurbær'),
        ('Grundarfjarðarbær', 'Grundarfjarðarbær'),
        ('Sveitarfélagið Hornafjörður', 'Sveitarfélagið Hornafjörður'),
        ('Bæjarhreppur', 'Bæjarhreppur'),
        ('Húnaþing vestra', 'Húnaþing vestra'),
        ('Seltjarnarnesbær', 'Seltjarnarnesbær'),
        ('Snæfellsbær', 'Snæfellsbær'),
        ('Vestmannaeyjabær', 'Vestmannaeyjabær'),
        ('Vesturbyggð', 'Vesturbyggð'),
        ('Ísafjarðarbær', 'Ísafjarðarbær'),
        ('Langanesbyggð', 'Langanesbyggð'),
        ('Kaldrananeshreppur', 'Kaldrananeshreppur'),
        ('Strandabyggð', 'Strandabyggð'),
        ('Tálknafjarðarhreppur', 'Tálknafjarðarhreppur'),
        ('Rangárþing ytra', 'Rangárþing ytra'),
        ('Breiðdalshreppur', 'Breiðdalshreppur'),
        ('Hveragerðisbær', 'Hveragerðisbær'),
        ('Sandgerðisbær', 'Sandgerðisbær'),
        ('Stykkishólmsbær', 'Stykkishólmsbær'),
        ('Sveitarfélagið Ölfus', 'Sveitarfélagið Ölfus'),
        ('Hvalfjarðarsveit', 'Hvalfjarðarsveit'),
        ('Eyjafjarðarsveit', 'Eyjafjarðarsveit'),
        ('Húnavatnshreppi', 'Húnavatnshreppi'),
        ('Rangárþing eystra', 'Rangárþing eystra'),
        ('Sveitarf. Skagaströnd', 'Sveitarf. Skagaströnd'),
        ('Grímsnes- og Grafningshreppur', 'Grímsnes- og Grafningshreppur'),
        ('Skaftárhreppur', 'Skaftárhreppur'),
        ('Mosfellsbær', 'Mosfellsbær'),
        ('Rangárþingi ytra', 'Rangárþingi ytra'),
        ('Eyja-og Miklaholtshreppur', 'Eyja-og Miklaholtshreppur'),
        ('Reykhólahreppur', 'Reykhólahreppur'),
        ('Skútustaðahreppur', 'Skútustaðahreppur'),
        ('Seyðisfjarðarkaupstaður', 'Seyðisfjarðarkaupstaður'),
        ('Þingeyjarsveit', 'Þingeyjarsveit'),
        ('Sveitarfélagið Vogar', 'Sveitarfélagið Vogar'),
        ('Súðavikurhreppur', 'Súðavikurhreppur'),
        ('Svalbarðsstrandarhreppur', 'Svalbarðsstrandarhreppur'),
        ('Mýrdalshreppur', 'Mýrdalshreppur'),
        ('Vopnafjarðarhreppur', 'Vopnafjarðarhreppur'),
        ('Hörgársveit', 'Hörgársveit'),
        ('Skeiða- og Gnúpverjahreppi', 'Skeiða- og Gnúpverjahreppi'),
        ('Hafnarfjarðarkaupstaður', 'Hafnarfjarðarkaupstaður'),
        ('Reykjanesbær', 'Reykjanesbær'),
        ('Garðabær', 'Garðabær'),
        ('Dalabyggð', 'Dalabyggð'),
        ('Reykjavíkurborg', 'Reykjavíkurborg'),
        ('Kópavogsbær', 'Kópavogsbær'),
        ('Dalvíkurbyggð', 'Dalvíkurbyggð'),
        ('Sveitarf. Skagafjörður', 'Sveitarf. Skagafjörður'),
        ('Sveitarfélagið Árborg', 'Sveitarfélagið Árborg'),
        ('Bláskógabyggð', 'Bláskógabyggð'),
        ('Blönduósbær', 'Blönduósbær'),
        ('Norðurþing', 'Norðurþing'),
        ('Akraneskaupstaður', 'Akraneskaupstaður'),
        ('Akureyrarkaupstaður', 'Akureyrarkaupstaður'),
        ('Fljótsdalshérað', 'Fljótsdalshérað'),
        ('Árneshreppur', 'Árneshreppur'),
        ('Flóahreppi', 'Flóahreppi'),
        ('Hrunamannahreppur', 'Hrunamannahreppur'),
        ('Sveitarfélagið Garður', 'Sveitarfélagið Garður'),
        ('Grýtubakkahreppur', 'Grýtubakkahreppur'),
        ('Bolungarvíkurkaupstaður', 'Bolungarvíkurkaupstaður'),
        ('Borgarbyggð', 'Borgarbyggð'),
        ('Borgarfjarðarhreppur', 'Borgarfjarðarhreppur'),
        ('Djúpavogshreppur', 'Djúpavogshreppur'),
        ('Fjarðabyggð', 'Fjarðabyggð'),
        ('Fjallabyggð', 'Fjallabyggð'),
        ('Grindavíkurbær', 'Grindavíkurbær'),
        ('Grundarfjarðarbær', 'Grundarfjarðarbær'),
        ('Sveitarfélagið Hornafjörður', 'Sveitarfélagið Hornafjörður'),
        ('Bæjarhreppur', 'Bæjarhreppur'),
        ('Húnaþing vestra', 'Húnaþing vestra'),
        ('Seltjarnarnesbær', 'Seltjarnarnesbær'),
        ('Snæfellsbær', 'Snæfellsbær'),
        ('Vestmannaeyjabær', 'Vestmannaeyjabær'),
        ('Vesturbyggð', 'Vesturbyggð'),
        ('Ísafjarðarbær', 'Ísafjarðarbær'),
        ('Langanesbyggð', 'Langanesbyggð'),
        ('Kaldrananeshreppur', 'Kaldrananeshreppur'),
        ('Strandabyggð', 'Strandabyggð'),
        ('Tálknafjarðarhreppur', 'Tálknafjarðarhreppur'),
        ('Rangárþing ytra', 'Rangárþing ytra'),
        ('Breiðdalshreppur', 'Breiðdalshreppur'),
        ('Hveragerðisbær', 'Hveragerðisbær'),
        ('Sandgerðisbær', 'Sandgerðisbær'),
        ('Stykkishólmsbær', 'Stykkishólmsbær'),
        ('Sveitarfélagið Ölfus', 'Sveitarfélagið Ölfus'),
        ('Hvalfjarðarsveit', 'Hvalfjarðarsveit'),
        ('Eyjafjarðarsveit', 'Eyjafjarðarsveit'),
        ('Húnavatnshreppi', 'Húnavatnshreppi'),
        ('Rangárþing eystra', 'Rangárþing eystra'),
        ('Sveitarf. Skagaströnd', 'Sveitarf. Skagaströnd'),
        ('Grímsnes- og Grafningshreppur', 'Grímsnes- og Grafningshreppur'),
        ('Skaftárhreppur', 'Skaftárhreppur'),
        ('Mosfellsbær', 'Mosfellsbær'),
        ('Rangárþingi ytra', 'Rangárþingi ytra'),
        ('Eyja-og Miklaholtshreppur', 'Eyja-og Miklaholtshreppur'),
        ('Reykhólahreppur', 'Reykhólahreppur'),
        ('Skútustaðahreppur', 'Skútustaðahreppur'),
        ('Seyðisfjarðarkaupstaður', 'Seyðisfjarðarkaupstaður'),
        ('Þingeyjarsveit', 'Þingeyjarsveit'),
        ('Sveitarfélagið Vogar', 'Sveitarfélagið Vogar'),
        ('Súðavikurhreppur', 'Súðavikurhreppur'),
        ('Svalbarðsstrandarhreppur', 'Svalbarðsstrandarhreppur'),
        ('Mýrdalshreppur', 'Mýrdalshreppur'),
        ('Vopnafjarðarhreppur', 'Vopnafjarðarhreppur'),
        ('Hörgársveit', 'Hörgársveit'),
        ('Skeiða- og Gnúpverjahreppi', 'Skeiða- og Gnúpverjahreppi'),
    )
    PARTS = (
        ('Ngr. Reykjavíkur', 'Ngr. Reykjavíkur'),
        ('Suðurnes', 'Suðurnes'),
        ('Vesturland', 'Vesturland'),
        ('Reykjavík', 'Reykjavík'),
        ('Norðurland eystra', 'Norðurland eystra'),
        ('Norðurland vestra', 'Norðurland vestra'),
        ('Suðurland', 'Suðurland'),
        ('Austurland', 'Austurland'),
        ('Vestfirðir', 'Vestfirðir'),
    )
    POST_CODES = (
        ('101', '101 (Reykjavík)'),
        ('103', '103 (Reykjavík)'),
        ('104', '104 (Reykjavík)'),
        ('105', '105 (Reykjavík)'),
        ('107', '107 (Reykjavík)'),
        ('108', '108 (Reykjavík)'),
        ('109', '109 (Reykjavík)'),
        ('110', '110 (Reykjavík)'),
        ('111', '111 (Reykjavík)'),
        ('112', '112 (Reykjavík)'),
        ('113', '113 (Reykjavík)'),
        ('116', '116 (Reykjavík)'),
        ('121', '121 (Reykjavík)'),
        ('123', '123 (Reykjavík)'),
        ('124', '124 (Reykjavík)'),
        ('125', '125 (Reykjavík)'),
        ('127', '127 (Reykjavík)'),
        ('128', '128 (Reykjavík)'),
        ('129', '129 (Reykjavík)'),
        ('130', '130 (Reykjavík)'),
        ('132', '132 (Reykjavík)'),
        ('170', '170 (Seltjarnarnesi)'),
        ('172', '172 (Seltjarnarnesi)'),
        ('190', '190 (Vogum)'),
        ('200', '200 (Kópavogi)'),
        ('201', '201 (Kópavogi)'),
        ('202', '202 (Kópavogi)'),
        ('203', '203 (Kópavogi)'),
        ('210', '210 (Garðabæ)'),
        ('212', '212 (Garðabæ)'),
        ('220', '220 (Hafnarfirði)'),
        ('221', '221 (Hafnarfirði)'),
        ('222', '222 (Hafnarfirði)'),
        ('225', '225 (Álftanesi)'),
        ('230', '230 (Reykjanesbæ)'),
        ('232', '232 (Reykjanesbæ)'),
        ('233', '233 (Reykjanesbæ)'),
        ('235', '235 (Reykjanesbæ)'),
        ('240', '240 (Grindavík)'),
        ('245', '245 (Sandgerði)'),
        ('250', '250 (Garði)'),
        ('260', '260 (Reykjanesbæ)'),
        ('270', '270 (Mosfellsbæ)'),
        ('271', '271 (Mosfellsbæ)'),
        ('276', '276 (Mosfellsbæ)'),
        ('300', '300 (Akranesi)'),
        ('301', '301 (Akranesi)'),
        ('302', '302 (Akranesi)'),
        ('310', '310 (Borgarnesi)'),
        ('311', '311 (Borgarnesi)'),
        ('320', '320 (Reykholt í Borgarfirði)'),
        ('340', '340 (Stykkishólmi)'),
        ('345', '345 (Flatey á Breiðafirði)'),
        ('350', '350 (Grundarfirði)'),
        ('355', '355 (Ólafsvík)'),
        ('356', '356 (Snæfellsbæ)'),
        ('360', '360 (Hellissandi)'),
        ('370', '370 (Búðardal)'),
        ('371', '371 (Búðardal)'),
        ('380', '380 (Reykhólahreppi)'),
        ('400', '400 (Ísafirði)'),
        ('401', '401 (Ísafirði)'),
        ('410', '410 (Hnífsdal)'),
        ('415', '415 (Bolungarvík)'),
        ('420', '420 (Súðavík)'),
        ('425', '425 (Flateyri)'),
        ('430', '430 (Suðureyri)'),
        ('450', '450 (Patreksfirði)'),
        ('451', '451 (Patreksfirði)'),
        ('460', '460 (Tálknafirði)'),
        ('465', '465 (Bíldudal)'),
        ('470', '470 (Þingeyri)'),
        ('471', '471 (Þingeyri)'),
        ('500', '500 (Stað)'),
        ('510', '510 (Hólmavík)'),
        ('512', '512 (Hólmavík)'),
        ('520', '520 (Drangsnesi)'),
        ('524', '524 (Árneshreppi)'),
        ('530', '530 (Hvammstanga)'),
        ('531', '531 (Hvammstanga)'),
        ('540', '540 (Blönduósi)'),
        ('541', '541 (Blönduósi)'),
        ('545', '545 (Skagaströnd)'),
        ('550', '550 (Sauðárkróki)'),
        ('551', '551 (Sauðárkróki)'),
        ('560', '560 (Varmahlíð)'),
        ('565', '565 (Hofsós)'),
        ('566', '566 (Hofsós)'),
        ('570', '570 (Fljótum)'),
        ('580', '580 (Siglufirði)'),
        ('600', '600 (Akureyri)'),
        ('601', '601 (Akureyri)'),
        ('602', '602 (Akureyri)'),
        ('603', '603 (Akureyri)'),
        ('610', '610 (Grenivík)'),
        ('611', '611 (Grímsey)'),
        ('620', '620 (Dalvík)'),
        ('621', '621 (Dalvík)'),
        ('625', '625 (Ólafsfirði)'),
        ('630', '630 (Hrísey)'),
        ('640', '640 (Húsavík)'),
        ('641', '641 (Húsavík)'),
        ('645', '645 (Fosshólli)'),
        ('650', '650 (Laugum)'),
        ('660', '660 (Mývatni)'),
        ('670', '670 (Kópaskeri)'),
        ('671', '671 (Kópaskeri)'),
        ('675', '675 (Raufarhöfn)'),
        ('680', '680 (Þórshöfn)'),
        ('681', '681 (Þórshöfn)'),
        ('685', '685 (Bakkafirði)'),
        ('690', '690 (Vopnafirði)'),
        ('700', '700 (Egilsstöðum)'),
        ('701', '701 (Egilsstöðum)'),
        ('710', '710 (Seyðisfirði)'),
        ('715', '715 (Mjóafirði)'),
        ('720', '720 (Borgarfirði (eystri))'),
        ('730', '730 (Reyðarfirði)'),
        ('735', '735 (Eskifirði)'),
        ('740', '740 (Neskaupstað)'),
        ('750', '750 (Fáskrúðsfirði)'),
        ('755', '755 (Stöðvarfirði)'),
        ('760', '760 (Breiðdalsvík)'),
        ('765', '765 (Djúpavogi)'),
        ('780', '780 (Höfn í Hornafirði)'),
        ('781', '781 (Höfn í Hornafirði)'),
        ('785', '785 (Öræfum)'),
        ('800', '800 (Selfossi)'),
        ('801', '801 (Selfossi)'),
        ('802', '802 (Selfossi)'),
        ('810', '810 (Hveragerði)'),
        ('815', '815 (Þorlákshöfn)'),
        ('816', '816 (Ölfus)'),
        ('820', '820 (Eyrarbakka)'),
        ('825', '825 (Stokkseyri)'),
        ('840', '840 (Laugarvatni)'),
        ('845', '845 (Flúðum)'),
        ('850', '850 (Hellu)'),
        ('851', '851 (Hellu)'),
        ('860', '860 (Hvolsvelli)'),
        ('861', '861 (Hvolsvelli)'),
        ('870', '870 (Vík)'),
        ('871', '871 (Vík)'),
        ('880', '880 (Kirkjubæjarklaustri)'),
        ('900', '900 (Vestmannaeyjum)'),
        ('902', '902 (Vestmannaeyjum)'),
    )

    name = models.CharField(max_length=128)
    ssn = models.CharField(max_length=10)
    managers = models.ManyToManyField(Manager, blank=True)
    teachers = models.ManyToManyField(Teacher, blank=True)
    students = models.ManyToManyField(Student, blank=True)
    school_nr = models.IntegerField(default=None, blank=True, null=True)

    address = models.CharField(max_length=256, blank=True, null=True)                              # Heimilisfang
    post_code = models.CharField(max_length=3, blank=True, null=True, choices=POST_CODES)          # Póstnúmer
    municipality = models.CharField(max_length=32, blank=True, null=True, choices=MUNICIPALITIES)  # Sveitarfélag
    part = models.CharField(max_length=24, blank=True, null=True, choices=PARTS)                   # Landshluti

    def __str__(self):
        return self.name + " (" + self.ssn + ")"

    def get_school_surveys(self):
        surveys = GroupSurvey.objects.filter(studentgroup__in=self.studentgroup_set.all())
        return surveys

    class Meta:
        ordering = ["name"]


class StudentGroup(models.Model):
    name = models.CharField(max_length=128)
    YEARS = (
        ('0', 'Blandaður árgangur'),
        ('1', '1. bekkur'),
        ('2', '2. bekkur'),
        ('3', '3. bekkur'),
        ('4', '4. bekkur'),
        ('5', '5. bekkur'),
        ('6', '6. bekkur'),
        ('7', '7. bekkur'),
        ('8', '8. bekkur'),
        ('9', '9. bekkur'),
        ('10', '10. bekkur'),
    )
    student_year = models.CharField(max_length=2, choices=YEARS, null=True, blank=True)
    group_managers = models.ManyToManyField(Teacher, blank=True)
    school = models.ForeignKey('School')
    students = models.ManyToManyField(Student, blank=True)

    def __str__(self):
        return self.name


class GroupSurvey(models.Model):
    studentgroup = models.ForeignKey(
        'StudentGroup', null=True, blank=True, on_delete=models.SET_NULL
    )
    survey = models.ForeignKey(Survey)
    active_from = models.DateField(default=timezone.now)
    active_to = models.DateField(default=timezone.now)

    def save(self, *args, **kwargs):
        if self.survey:
            self.active_from = self.survey.active_from
            self.active_to = self.survey.active_to
        super(GroupSurvey, self).save(*args, **kwargs)

    def is_expired(self):
        if timezone.now().date() > self.active_to:
            return True
        return False

    def results(self):
        return SurveyResult.objects.filter(survey=self)

    def title(self):
        if self.survey:
            return self.survey.title
        else:
            return ""

    def __str__(self):
        return self.survey.title


class SurveyResult(models.Model):
    student = models.ForeignKey('Student')
    created_at = models.DateTimeField(default=timezone.now)
    results = models.TextField()
    reported_by = models.ForeignKey(
        'Teacher', null=True, blank=True, on_delete=models.SET_NULL
    )
    survey = models.ForeignKey(
        'GroupSurvey', null=True, blank=True, on_delete=models.SET_NULL
    )
    created_at = models.DateField(default=timezone.now)

    @classmethod
    def get_results(cls, id):
        return json.loads(cls(pk=id).results)


class SurveyLogin(models.Model):
    student = models.ForeignKey(Student)
    survey_id = models.CharField(max_length=256)  # external survey identity
    survey_code = models.CharField(max_length=16)


# Prófadæmi, spurningar
class ExampleSurveyQuestion(models.Model):
    quiz_type_choices = (
        ('STÆ', 'Stærðfræði'),
        ('ENS', 'Enska'),
        ('ÍSL', 'Íslenska'),
    )
    category_choices = (
        ('RA', 'Reikningur og aðgerðir'),
        ('RM', 'Rúmfræði'),
        ('TT', 'Tölur og talnaskilningur'),
        ('AL', 'Algebra'),
        ('HP', 'Hlutföll og prósentur'),
        ('LE', 'Lesskilningur'),
        ('MN', 'Málnotkun'),
    )
    created_by = models.ForeignKey(User, null=True)
    # flýtikóði
    quickcode = models.CharField(max_length=16, unique=True)
    # próftegund
    quiz_type = models.CharField(max_length=3, choices=quiz_type_choices)
    # flokkur
    category = models.CharField(max_length=2, choices=category_choices)
    # ĺýsing
    description = models.TextField()
    # dæmi
    example = FroalaField()

    def answers_total(self):
        return self.examplesurveyanswer_set.count()

    def answers_correct_pct(self):
        answers_total = self.answers_total()

        if answers_total == 0:
            return "0%"
        answers_correct = self.examplesurveyanswer_set.filter(answer=True).count()

        return "{:.1f}%".format((answers_correct / answers_total) * 100)


# Prófadæmi, svör
class ExampleSurveyAnswer(models.Model):
    # nemandi
    student = models.ForeignKey(Student)
    # spurning
    question = models.ForeignKey(ExampleSurveyQuestion)
    # próf
    groupsurvey = models.ForeignKey(GroupSurvey, null=True)
    exam_code = models.CharField(max_length=128, null=True)
    # dags
    date = models.DateField(default=timezone.now)
    # Svar (rétt/rangt)
    answer = models.BooleanField()
