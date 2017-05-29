# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

from django.contrib.auth.models import User
from django.contrib.postgres.fields import JSONField
from django.utils import timezone

import json

from froala_editor.fields import FroalaField

from survey.models import Survey


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
        ('101', '101'), ('103', '103'), ('104', '104'), ('105', '105'), ('107', '107'), ('108', '108'), ('109', '109'),
        ('110', '110'), ('111', '111'), ('112', '112'), ('113', '113'), ('116', '116'), ('121', '121'), ('123', '123'),
        ('124', '124'), ('125', '125'), ('127', '127'), ('128', '128'), ('129', '129'), ('130', '130'), ('132', '132'),
        ('170', '170'), ('172', '172'), ('190', '190'), ('200', '200'), ('201', '201'), ('202', '202'), ('203', '203'),
        ('210', '210'), ('212', '212'), ('220', '220'), ('221', '221'), ('222', '222'), ('225', '225'), ('230', '230'),
        ('232', '232'), ('233', '233'), ('235', '235'), ('240', '240'), ('245', '245'), ('250', '250'), ('260', '260'),
        ('270', '270'), ('271', '271'), ('276', '276'), ('300', '300'), ('301', '301'), ('302', '302'), ('310', '310'),
        ('311', '311'), ('320', '320'), ('340', '340'), ('345', '345'), ('350', '350'), ('355', '355'), ('356', '356'),
        ('360', '360'), ('370', '370'), ('371', '371'), ('380', '380'), ('400', '400'), ('401', '401'), ('410', '410'),
        ('415', '415'), ('420', '420'), ('425', '425'), ('430', '430'), ('450', '450'), ('451', '451'), ('460', '460'),
        ('465', '465'), ('470', '470'), ('471', '471'), ('500', '500'), ('510', '510'), ('512', '512'), ('520', '520'),
        ('524', '524'), ('530', '530'), ('531', '531'), ('540', '540'), ('541', '541'), ('545', '545'), ('550', '550'),
        ('551', '551'), ('560', '560'), ('565', '565'), ('566', '566'), ('570', '570'), ('580', '580'), ('600', '600'),
        ('601', '601'), ('602', '602'), ('603', '603'), ('610', '610'), ('611', '611'), ('620', '620'), ('621', '621'),
        ('625', '625'), ('630', '630'), ('640', '640'), ('641', '641'), ('645', '645'), ('650', '650'), ('660', '660'),
        ('670', '670'), ('671', '671'), ('675', '675'), ('680', '680'), ('681', '681'), ('685', '685'), ('690', '690'),
        ('700', '700'), ('701', '701'), ('710', '710'), ('715', '715'), ('720', '720'), ('730', '730'), ('735', '735'),
        ('740', '740'), ('750', '750'), ('755', '755'), ('760', '760'), ('765', '765'), ('780', '780'), ('781', '781'),
        ('785', '785'), ('800', '800'), ('801', '801'), ('802', '802'), ('810', '810'), ('815', '815'), ('816', '816'),
        ('820', '820'), ('825', '825'), ('840', '840'), ('845', '845'), ('850', '850'), ('851', '851'), ('860', '860'),
        ('861', '861'), ('870', '870'), ('871', '871'), ('880', '880'), ('900', '900'), ('902', '902'),
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

    def is_open(self):
        curdate = timezone.now().date()

        if curdate < self.active_to and curdate > self.active_from:
            return True
        else:
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
    student = models.ForeignKey('Student', null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(default=timezone.now)
    results = JSONField(null=True, blank=True)
    reported_by = models.ForeignKey('Teacher', null=True, blank=True, on_delete=models.SET_NULL)
    survey = models.ForeignKey('GroupSurvey', null=True, blank=True, on_delete=models.CASCADE)
    created_at = models.DateField(default=timezone.now)

    class Meta:
        unique_together = (("student", "survey"))

    def _lesskilnings_results(self, input_values):
        '''
        Skilum niðurstöðum prófs í lesskilningi
        '''
        # Cycle through input_values, sum up all values where the key starts with
        # 'hljod_', 'mal_', 'bok_'. Checks for input errors.
        lesskilnings_sums = {'hljod_': 0, 'mal_': 0, 'bok_': 0}
        for key, value in input_values.items():
            for type_sum in lesskilnings_sums.keys():
                # type = 'hljod_' for instance, type_sum for 'hljod_' starts as 0
                if key.startswith(type_sum):
                    if not str(value).isdigit():
                        # Input error so we will make this type_sum permanently = -1 to indicate error
                        lesskilnings_sums[type_sum] = -1
                    elif str(value).isdigit() and not lesskilnings_sums[type_sum] == -1:
                        # Not input error so let's add up
                        lesskilnings_sums[type_sum] += int(value)

        hopar = []
        if lesskilnings_sums["hljod_"] == -1:
            hopar.append('Vantar gögn')
        elif lesskilnings_sums["hljod_"] <= 14:
            hopar.append('Áhætta 1')
        elif lesskilnings_sums["hljod_"] <= 17:
            hopar.append('Áhætta 2')
        elif lesskilnings_sums["hljod_"] <= 19:
            hopar.append('Óvissa')
        else:
            hopar.append('Utan áhættu')

        if lesskilnings_sums["mal_"] == -1:
            hopar.append('Vantar gögn')
        elif lesskilnings_sums["mal_"] <= 14:
            hopar.append('Áhætta 1')
        elif lesskilnings_sums["mal_"] <= 16:
            hopar.append('Áhætta 2')
        elif lesskilnings_sums["mal_"] <= 17:
            hopar.append('Óvissa')
        else:
            hopar.append('Utan áhættu')

        if lesskilnings_sums["bok_"] == -1:
            hopar.append('Vantar gögn')
        elif lesskilnings_sums["bok_"] <= 7:
            hopar.append('Áhætta 1')
        elif lesskilnings_sums["bok_"] <= 10:
            hopar.append('Áhætta 2')
        elif lesskilnings_sums["bok_"] <= 12:
            hopar.append('Óvissa')
        else:
            hopar.append('Utan áhættu')

        return hopar

    def _lesfimi_results(self, click_values, transformation):
        try:
            villur = len(click_values) - 1

            if (villur < 3):
                villur = 0
            elif(villur < 10):
                villur -= 2
            else:
                villur *= 2
                villur -= 11

            last_word_num = int(click_values[-1].split(',')[0])
            vegin_oam = last_word_num - villur
            vegin_oam = int(round(vegin_oam / 2))

            if (transformation):
                data = transformation.data
                vegin_oam = data[str(vegin_oam)]

            if vegin_oam < 0:
                vegin_oam = 0

            return [vegin_oam]
        except:
            return [""]

    def calculated_results(self, use_transformation=True):
        survey_type = self.survey.survey.survey_type.title

        if survey_type == 'Lesskimun':
            return self._lesskilnings_results(self.results['input_values'])
        elif survey_type == 'Lesfimi':
            transformation = None
            if use_transformation:
                if self.survey.survey.surveytransformation_set.exists():
                    transformation = self.survey.survey.surveytransformation_set.first()
            return self._lesfimi_results(self.results['click_values'], transformation)
        else:
            return self.results['click_values']

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
