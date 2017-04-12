# -*- coding: utf-8 -*-
from __future__   import unicode_literals

from django.db    import models
from django       import forms
from django.utils import timezone
from jsonfield    import JSONField

from common.models import Student


_YEAR_IN_SCHOOL_CHOICES = (
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

class _SamraemdBaseModel(models.Model):
    student = models.ForeignKey(Student)
    exam_date = models.DateField()
    
    class Meta:
        abstract = True


class _SamraemdStudentYear(models.Model):
    student_year = models.CharField(
        max_length=2,
        choices=_YEAR_IN_SCHOOL_CHOICES,
    )

    class Meta:
        abstract = True


class SamraemdMathResult(_SamraemdBaseModel, _SamraemdStudentYear):
    # data fields
    # Hæfnieinkunn (A, B+, B, C+, C, D)
    he    = models.CharField(max_length = 2, default='', blank=True)

    # Samræmd einkunn (0-10)
    ra_se = models.CharField(max_length = 4, default='') # Reikningur og aðgerðir, samræmd einkunn
    rm_se = models.CharField(max_length = 4, default='') # Rúmfræði, samræmd einkunn
    tt_se = models.CharField(max_length = 4, default='') # Tölur og talnaskilningur, samræmd einkunn
    se    = models.CharField(max_length = 4, default='') # Samræmd einkunn
    # Raðeinkunn (1-100)
    hp_re = models.CharField(max_length = 4, default='') # Hlutföll og prósentur
    al_re = models.CharField(max_length = 4, default='') # Algebra, raðeinkunn
    ra_re = models.CharField(max_length = 4, default='') # Reikningur og aðgerðir, raðeinkunn
    rm_re = models.CharField(max_length = 4, default='') # Rúmfræði, raðeinkunn
    tt_re = models.CharField(max_length = 4, default='') # Tölur og talnaskilningur, raðeinkunn
    re    = models.CharField(max_length = 4, default='') # Raðeinkunn
    # Grunnskólaeinkunn
    hp_sg         = models.CharField(max_length = 4, default='', blank=True) # Hlutföll og prósentur, grunnskólaeinkunn
    al_sg         = models.CharField(max_length = 4, default='', blank=True) # Algebra, grunnskólaeinkunn
    ra_sg         = models.CharField(max_length = 4, default='', blank=True) # Reikningur og aðgerðir, grunnskólaeinkunn
    rm_sg         = models.CharField(max_length = 4, default='', blank=True) # Rúmfræði, grunnskólaeinkunn
    tt_sg         = models.CharField(max_length = 4, default='', blank=True) # Tölur og talnaskilningur, grunnskólaeinkunn
    sg            = models.CharField(max_length = 4, default='', blank=True) # Grunnskólaeinkunn
    ord_talna_txt = models.CharField(max_length = 128)
    # Framfaraeinkunn
    fm_fl  = models.CharField(max_length = 32, blank=True)
    fm_txt = models.CharField(max_length = 256, blank=True)
    # exam fields
    exam_code = models.CharField(max_length = 128)


class _SamraemdLANGResult(_SamraemdBaseModel, _SamraemdStudentYear):
    # data fields
    # Hæfnieinkunn (A, B, C, D)
    he = models.CharField(max_length = 2, default='', blank=True)    # Hæfnieinkunn
    # Samræmd einkunn (0-10)
    le_se = models.CharField(max_length = 4, default='', blank=True) # Lesskilningur, samræmd einkunn
    mn_se = models.CharField(max_length = 4, default='', blank=True) # Málnotkun, samræmd einkunn
    ri_se = models.CharField(max_length = 4, default='', blank=True) # Ritun, samræmd einkunn
    se    = models.CharField(max_length = 4, default='', blank=True) # Samræmd einkunn
    # Raðeinkunn (1-100)
    le_re = models.CharField(max_length = 4, default='', blank=True) # Lesskilningur, raðeinkunn
    mn_re = models.CharField(max_length = 4, default='', blank=True) # Málnotkun, raðeinkunn
    ri_re = models.CharField(max_length = 4, default='', blank=True) # Ritun, raðeinkunn
    re    = models.CharField(max_length = 4, default='', blank=True) # Raðeinkunn
    # Grunnskólaeinkunn
    le_sg = models.CharField(max_length = 4, default='', blank=True) # Lesskilningur, grunnskólaeinkunn
    mn_sg = models.CharField(max_length = 4, default='', blank=True) # Málnotkun, grunnskólaeinkunn
    ri_sg = models.CharField(max_length = 4, default='', blank=True) # Ritun, grunnskólaeinkunn
    sg    = models.CharField(max_length = 4, default='', blank=True) # Grunnskólaeinkunn
    # Framfaraeinkunn
    fm_fl  = models.CharField(max_length = 32, blank=True)
    fm_txt = models.CharField(max_length = 256, blank=True)

    exam_code = models.CharField(max_length = 128)

    class Meta:
        abstract = True


class SamraemdISLResult(_SamraemdLANGResult):
    pass


class SamraemdENSResult(_SamraemdLANGResult):
    pass


class SamraemdResult(_SamraemdBaseModel):
    CODES   = (
        (1, 'Íslenska'),
        (2, 'Enska'),
        (3, 'Stærðfræði'),
    )

    exam_code = models.CharField(max_length=2, choices=CODES, null=True)
    exam_name = models.CharField(max_length=125, null=True)
    student_year = models.CharField(
        max_length=2,
        choices=_YEAR_IN_SCHOOL_CHOICES,
        null=True
    )

    result_data   = JSONField()
    result_length = models.CharField(max_length=4)
