from django                     import forms
from django.forms.widgets       import SelectDateWidget
from django.utils.translation   import ugettext_lazy as _

from . import models


class SurveyTypeForm(forms.ModelForm):
    """docstring for SurveyTypeForm"""
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
            months=MONTHS,
            attrs={
                'class': 'required',
            })
        self.fields['active_to'].widget = SelectDateWidget(
            empty_label=("Ár", "Mánuður", "Dagur"),
            months=MONTHS,
            attrs={
                'class': 'required',
            })

    class Meta:
        model  = models.Survey
        fields = ['identifier', 'title', 'survey_type', 'description', 'active_from', 'active_to']
        labels = {
            'identifier' : 'Auðkenni',
            'title'      : 'Heiti',
            'survey_type': 'Tegund',
            'description': 'Lýsing',
            'active_from': 'Virkt frá',
            'active_to'  : 'Virkt til',
        }


class SurveyResourceForm(forms.ModelForm):
    class Meta:
        model  = models.SurveyResource
        fields = ['title', 'resource_url', 'description']
        labels = {
            'title'       : 'Titill',
            'resource_url': 'Vefslóð',
            'description' : 'Lýsing',
        }


class SurveyGradingTemplateForm(forms.ModelForm):
    class Meta:
        model  = models.SurveyGradingTemplate
        fields = ['md', 'info']
        labels = {
            'md'  :  'MarkDown kóði',
            'info': 'Leiðbeiningar',
        }


class SurveyInputFieldForm(forms.ModelForm):
    class Meta:
        model  = models.SurveyInputField
        fields = ['input_group', 'name', 'label']
        labels = {
            'input_group': 'Flokkur',
            'name'       : 'Tæknilegt heiti',
            'label'      : 'Sýnilegt heiti',
        }


class SurveyInputGroupForm(forms.ModelForm):
    class Meta:
        model  = models.SurveyInputGroup
        fields = ['title', 'description']
        labels = {
            'title'      : 'Heiti',
            'description': 'Lýsing'
        }
