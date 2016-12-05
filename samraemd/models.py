# -*- coding: utf-8 -*-
from __future__   import unicode_literals

from django.db    import models
from django       import forms
from django.utils import timezone
from jsonfield    import JSONField

from common.models import Student


class SamraemdMathResult(models.Model):
    student = models.ForeignKey(Student)
    # data fields
    # Samræmd einkunn
    ra_se = models.CharField(max_length = 4)
    rm_se = models.CharField(max_length = 4)
    tt_se = models.CharField(max_length = 4)
    se    = models.CharField(max_length = 4)
    # Raðeinkunn
    ra_re = models.CharField(max_length=4)
    rm_re = models.CharField(max_length=4)
    tt_re = models.CharField(max_length=4)
    re    = models.CharField(max_length=4)
    # Grunnskólaeinkunn
    ra_sg         = models.CharField(max_length=4)
    rm_sg         = models.CharField(max_length=4)
    tt_sg         = models.CharField(max_length=4)
    sg            = models.CharField(max_length=4)
    ord_talna_txt = models.CharField(max_length = 128)
    # Framfaraeinkunn
    fm_fl  = models.CharField(max_length=4, blank=True)
    fm_txt = models.CharField(max_length = 256, blank=True)
    # exam fields
    exam_code = models.CharField(max_length = 128)
    exam_date = models.DateField()
    YEAR_IN_SCHOOL_CHOICES = (
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
    student_year = models.CharField(
        max_length=2,
        choices=YEAR_IN_SCHOOL_CHOICES,
    )


class SamraemdMathResultForm(forms.ModelForm):
    file = forms.FileField()

    class Meta:
        model = SamraemdMathResult
        fields = [
            'ra_se', 'rm_se', 'tt_se', 'se', 'ra_re', 'rm_re', 'tt_re', 're',
            'ra_sg', 'rm_sg', 'tt_sg', 'sg', 'ord_talna_txt', 'fm_fl', 'fm_txt',
            'exam_code', 'exam_date', 'student_year'
        ]
        labels = {
            'exam_code'    : 'Prófkóði',
            'student'      : 'Nemandi',
            'ra_se'        : 'Samræmd einkunn - Reikningur og aðgerðir',
            'rm_se'        : 'Samræmd einkunn - Rúmfræði og mælingar',
            'tt_se'        : 'Samræmd einkunn - Tölur og talnaskilningur',
            'se'           : 'Samræmd einkunn - Heild',
            'ra_re'        : 'Raðeinkunn - Reikningur og aðgerðir',
            'rm_re'        : 'Raðeinkunn - Rúmfræði og mælingar',
            'tt_re'        : 'Raðeinkunn - Tölur og talnaskilningur',
            're'           : 'Raðeinkunn - Heild',
            'ra_sg'        : 'Grunnskólaeinkunn - Reikningur og aðgerðir',
            'rm_sg'        : 'Grunnskólaeinkunn - Rúmfræði og mælingar',
            'tt_sg'        : 'Grunnskólaeinkunn - Tölur og talnaskilningur',
            'sg'           : 'Grunnskólaeinkunn - Heild',
            'ord_talna_txt': 'Orðadæmi og talnadæmi',
            'fm_fl'        : 'Framfaraflokkur',
            'fm_txt'       : 'Framfaratexti',
            'exam_date'    : 'Dagsetning prófs (YYYY-MM-DD)',
            'student_year' : 'Árgangur'
        }


class SamraemdISLResult(models.Model):
    student = models.ForeignKey(Student)
    # data fields
    # Samræmd einkunn
    le_se = models.CharField(max_length=4)
    mn_se = models.CharField(max_length=4)
    ri_se = models.CharField(max_length=4)
    se    = models.CharField(max_length=4)
    # Raðeinkunn
    le_re = models.CharField(max_length=4)
    mn_re = models.CharField(max_length=4)
    ri_re = models.CharField(max_length=4)
    re    = models.CharField(max_length=4)
    # Grunnskólaeinkunn
    le_sg = models.CharField(max_length=4)
    mn_sg = models.CharField(max_length=4)
    ri_sg = models.CharField(max_length=4)
    sg    = models.CharField(max_length=4)
    # Framfaraeinkunn
    fm_fl  = models.CharField(max_length=4, blank=True)
    fm_txt = models.CharField(max_length = 256, blank=True)
    # exam fields
    exam_code = models.CharField(max_length = 256)
    exam_date = models.DateField()
    YEAR_IN_SCHOOL_CHOICES = (
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
    student_year = models.CharField(
        max_length=2,
        choices=YEAR_IN_SCHOOL_CHOICES,
    )


class SamraemdISLResultForm(forms.ModelForm):
    file = forms.FileField()

    class Meta:
        model = SamraemdISLResult
        fields = [
            'le_se', 'mn_se', 'ri_se', 'se', 'le_re', 'mn_re', 'ri_re', 're',
            'le_sg', 'mn_sg', 'ri_sg', 'sg', 'fm_fl', 'fm_txt',
            'exam_code', 'exam_date', 'student_year'
        ]
        labels = {
            'exam_code'   : 'Prófkóði',
            'student'     : 'Nemandi',
            'le_se'       : 'Samræmd einkunn - Lestur',
            'mn_se'       : 'Samræmd einkunn - Málnotkun',
            'ri_se'       : 'Samræmd einkunn - Ritun',
            'se'          : 'Samræmd einkunn - Heild',
            'le_re'       : 'Raðeinkunn - Lestur',
            'mn_re'       : 'Raðeinkunn - Málnotkun',
            'ri_re'       : 'Raðeinkunn - Ritun',
            're'          : 'Raðeinkunn - Heild',
            'le_sg'       : 'Grunnskólaeinkunn - Lestur',
            'mn_sg'       : 'Grunnskólaeinkunn - Málnotkun',
            'ri_sg'       : 'Grunnskólaeinkunn - Ritun',
            'sg'          : 'Grunnskólaeinkunn - Heild',
            'fm_fl'       : 'Framfaraflokkur',
            'fm_txt'      : 'Framfaratexti',
            'exam_date'   : 'Dagsetning prófs (YYYY-MM-DD)',
            'student_year': 'Árgangur'
        }


class SamraemdResult(models.Model):
    student = models.ForeignKey(Student)
    CODES   = (
        (1, 'Íslenska'),
        (2, 'Enska'),
        (3, 'Stærðfræði'),
    )
    exam_code = models.CharField(max_length=2, choices=CODES, null=True)
    exam_name = models.CharField(max_length=125, null=True)
    exam_date = models.DateField(default=timezone.now)
    YEAR_IN_SCHOOL_CHOICES = (
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
    student_year = models.CharField(
        max_length=2,
        choices=YEAR_IN_SCHOOL_CHOICES,
        null=True
    )
    result_data   = JSONField()
    result_length = models.CharField(max_length=4)


class SamraemdResultForm(forms.ModelForm):
    file = forms.FileField()

    class Meta:
        model = SamraemdResult
        fields = ['student', 'exam_code', 'exam_date', 'exam_name', 'result_data', 'result_length']
        labels = {
            'student'      : 'Nemandi',
            'exam_code'    : 'Próf',
            'exam_name'    : 'Heiti',
            'exam_date'    : 'Dagsetning',
            'result_data'  : 'Gögn',
            'result_length': 'Fjöldi spurninga'
        }
