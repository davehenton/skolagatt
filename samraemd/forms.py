from django import forms

from samraemd.models import (
	SamraemdMathResult,
	SamraemdISLResult,
	SamraemdENSResult,
	SamraemdResult,
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


class SamraemdENSResultForm(forms.ModelForm):
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
