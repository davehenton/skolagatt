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
    fm_fl  = models.CharField(max_length = 32, blank=True)
    fm_txt = models.CharField(max_length = 256, blank=True)
    # exam fields
    exam_code = models.CharField(max_length = 128)


class _SamraemdLANGResult(_SamraemdBaseModel, _SamraemdStudentYear):
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
