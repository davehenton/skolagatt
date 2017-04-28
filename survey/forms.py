from django import forms
from django.forms.widgets import SelectDateWidget
from django.forms import (
    MultipleChoiceField,
    BooleanField,
)
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone

from . import models

from common.util import add_field_classes


class SurveyTypeForm(forms.ModelForm):
    """docstring for SurveyTypeForm"""

    def __init__(self, *args, **kwargs):
        super(SurveyTypeForm, self).__init__(*args, **kwargs)
        add_field_classes(self, self.fields)

    class Meta:
        model = models.SurveyType
        fields = ['identifier', 'title', 'description']
        labels = {
            'idendifier': 'Auðkenni',
            'title': 'Heiti',
            'description': 'Lýsing'
        }


class SurveyForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(SurveyForm, self).__init__(*args, **kwargs)
        MONTHS = {
            1: _('jan'), 2: _('feb'), 3: _('mar'), 4: _('apr'),
            5: _('maí'), 6: _('jún'), 7: _('júl'), 8: _('ágú'),
            9: _('sep'), 10: _('okt'), 11: _('nóv'), 12: _('des')
        }
        self.fields['active_from'].widget = SelectDateWidget(
            empty_label=("Ár", "Mánuður", "Dagur"),
            years=range(2016, timezone.now().year + 10),
            months=MONTHS,
            attrs={
                'class': 'required form-control',
                'style': 'width: 26%; display: inline-block;'
            })
        self.fields['active_to'].widget = SelectDateWidget(
            empty_label=("Ár", "Mánuður", "Dagur"),
            years=range(2016, timezone.now().year + 10),
            months=MONTHS,
            attrs={
                'class': 'required form-control',
                'style': 'width: 26%; display: inline-block;'
            })
        fields = [
            'identifier', 'title', 'survey_type', 'student_year', 'description'
        ]
        add_field_classes(self, fields)

    class Meta:
        model = models.Survey
        fields = [
            'identifier', 'title', 'survey_type', 'student_year',
            'description', 'active_from', 'active_to'
        ]
        labels = {
            'identifier': 'Auðkenni',
            'title': 'Heiti',
            'survey_type': 'Tegund',
            'student_year': 'Árgangur',
            'description': 'Lýsing',
            'active_from': 'Virkt frá',
            'active_to': 'Virkt til',
        }


class SurveyCreateMultiForm(SurveyForm):
    STUDENT_YEAR_CHOICES = (
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
    student_year = MultipleChoiceField(choices=STUDENT_YEAR_CHOICES)
    mandatory = BooleanField(initial=True)

    def __init__(self, *args, **kwargs):
        super(SurveyCreateMultiForm, self).__init__(*args, **kwargs)
        self.fields['identifier'].widget.attrs = {
            'class': 'form-control',
            'placeholder': 'b%student_year%_AB_monYY',
        }
        self.fields['title'].widget.attrs = {
            'class': 'form-control',
            'placeholder': '%student_year%. bekkur - Próftegund - mánuður',
        }
        self.fields['mandatory'].label = 'Óvalkvæmt (búa til bekkjarpróf)'


class SurveyResourceForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(SurveyResourceForm, self).__init__(*args, **kwargs)
        add_field_classes(self, self.fields)

    class Meta:
        model = models.SurveyResource
        fields = ['title', 'description', 'resource_html', 'resource_url']
        labels = {
            'title': 'Titill',
            'resource_url': 'Vefslóð á prófgagn*',
            'description': 'Lýsing',
            'resource_html': 'Meginmál',
        }


class SurveyGradingTemplateForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(SurveyGradingTemplateForm, self).__init__(*args, **kwargs)
        add_field_classes(self, self.fields)

    class Meta:
        model = models.SurveyGradingTemplate
        fields = ['title', 'md', 'info']
        labels = {
            'title': 'Titill',
            'md': 'MarkDown kóði',
            'info': 'Leiðbeiningar',
        }


class SurveyInputFieldForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(SurveyInputFieldForm, self).__init__(*args, **kwargs)
        add_field_classes(self, self.fields)

    class Meta:
        model = models.SurveyInputField
        fields = ['input_group', 'name', 'label']
        labels = {
            'input_group': 'Flokkur',
            'name': 'Tæknilegt heiti',
            'label': 'Sýnilegt heiti',
        }


class SurveyInputGroupForm(forms.ModelForm):
    create_for_family = BooleanField(initial=False)

    def __init__(self, *args, **kwargs):
        super(SurveyInputGroupForm, self).__init__(*args, **kwargs)
        add_field_classes(self, self.fields)

    class Meta:
        model = models.SurveyInputGroup
        fields = ['title', 'identifier', 'description', 'create_for_family']
        labels = {
            'title': 'Heiti',
            'identifier': 'Kenni',
            'description': 'Lýsing',
            'create_for_family': 'Á við öll próf sem voru gerð á sama tíma',
        }


class SurveyInputGroupCreateForm(SurveyInputGroupForm):
    def __init__(self, *args, **kwargs):
        super(SurveyInputGroupCreateForm, self).__init__(*args, **kwargs)


class SurveyTransformationForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(SurveyTransformationForm, self).__init__(*args, **kwargs)
        add_field_classes(self, self.fields)

    class Meta:
        model = models.SurveyTransformation
        fields = ['name', 'unit']
        labels = {
            'name': 'Nafn',
            'unit': 'Eining',
        }
