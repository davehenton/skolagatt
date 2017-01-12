from django                     import forms
from django.forms.widgets       import SelectDateWidget
from django.utils.translation   import ugettext_lazy as _
from django.utils               import timezone

from . import models

from common.util import add_field_classes


class SurveyTypeForm(forms.ModelForm):
    """docstring for SurveyTypeForm"""
    def __init__(self, *args, **kwargs):
        super(SurveyTypeForm, self).__init__(*args, **kwargs)
        add_field_classes(self, self.fields)

    class Meta:
        model  = models.SurveyType
        fields = ['identifier', 'title', 'description']
        labels = {
            'idendifier' : 'Auðkenni',
            'title'      : 'Heiti',
            'description': 'Lýsing'
        }


class SurveyForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(SurveyForm, self).__init__(*args, **kwargs)
        MONTHS = {
            1: _('jan'),  2: _('feb'),  3: _('mar'),  4: _('apr'),
            5: _('maí'),  6: _('jún'),  7: _('júl'),  8: _('ágú'),
            9: _('sep'), 10: _('okt'), 11: _('nóv'), 12: _('des')
        }
        self.fields['active_from'].widget = SelectDateWidget(
            empty_label=("Ár", "Mánuður", "Dagur"),
            years = range(2016, timezone.now().year + 10),
            months=MONTHS,
            attrs={
                'class': 'required form-control',
                'style': 'width: 26%; display: inline-block;'
            })
        self.fields['active_to'].widget = SelectDateWidget(
            empty_label=("Ár", "Mánuður", "Dagur"),
            years = range(2016, timezone.now().year + 10),
            months=MONTHS,
            attrs={
                'class': 'required form-control',
                'style': 'width: 26%; display: inline-block;'
            })
        self.fields['support_and_exception_deadline'].widget = SelectDateWidget(
            empty_label=("Ár", "Mánuður", "Dagur"),
            years = range(2016, timezone.now().year + 10),
            months=MONTHS,
            attrs={
                'class': 'form-control disabled',
                'style': 'width: 26%; display: inline-block;',
                'disabled': True,
            })
        fields = [
            'identifier', 'title', 'survey_type', 'student_year', 'description',
            'support_and_exception_allowed',
        ]
        add_field_classes(self, fields)

    class Meta:
        model  = models.Survey
        fields = [
            'identifier', 'title', 'survey_type', 'student_year',
            'description', 'active_from', 'active_to', 'support_and_exception_deadline',
            'support_and_exception_allowed',
        ]
        labels = {
            'identifier'                     : 'Auðkenni',
            'title'                          : 'Heiti',
            'survey_type'                    : 'Tegund',
            'student_year'                   : 'Árgangur',
            'description'                    : 'Lýsing',
            'active_from'                    : 'Virkt frá',
            'active_to'                      : 'Virkt til',
            'support_and_exception_allowed'  : 'Undanþágur og stuðningsúrræði leyfð',
            'support_and_exception_deadline' : 'Skráningarfrestur undanþága og stuðningsúrræða',
        }


class SurveyResourceForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(SurveyResourceForm, self).__init__(*args, **kwargs)
        add_field_classes(self, self.fields)

    class Meta:
        model  = models.SurveyResource
        fields = ['title', 'resource_url', 'description']
        labels = {
            'title'       : 'Titill',
            'resource_url': 'Vefslóð',
            'description' : 'Lýsing',
        }


class SurveyGradingTemplateForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(SurveyGradingTemplateForm, self).__init__(*args, **kwargs)
        add_field_classes(self, self.fields)

    class Meta:
        model  = models.SurveyGradingTemplate
        fields = ['title', 'md', 'info']
        labels = {
            'title': 'Titill',
            'md'   : 'MarkDown kóði',
            'info' : 'Leiðbeiningar',
        }


class SurveyInputFieldForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(SurveyInputFieldForm, self).__init__(*args, **kwargs)
        add_field_classes(self, self.fields)

    class Meta:
        model  = models.SurveyInputField
        fields = ['input_group', 'name', 'label']
        labels = {
            'input_group': 'Flokkur',
            'name'       : 'Tæknilegt heiti',
            'label'      : 'Sýnilegt heiti',
        }


class SurveyInputGroupForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(SurveyInputGroupForm, self).__init__(*args, **kwargs)
        add_field_classes(self, self.fields)

    class Meta:
        model  = models.SurveyInputGroup
        fields = ['title', 'identifier', 'description']
        labels = {
            'title'      : 'Heiti',
            'identifier' : 'Kenni',
            'description': 'Lýsing'
        }


class SurveyInputGroupCreateForm(SurveyInputGroupForm):
    def __init__(self, *args, **kwargs):
        super(SurveyInputGroupCreateForm, self).__init__(*args, **kwargs)
