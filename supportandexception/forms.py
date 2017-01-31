 # -*- coding: utf-8 -*-
from django import forms
from .models import SupportResource, Exceptions


class UploadFileForm(forms.Form):
    file = forms.FileField()


support_title = (
    ('reading_assistance', 'Lestraraðstoð'),
    ('interpretation', 'Túlkun fyrirmæla'),
    ('longer_time', 'Lengdur próftími'),
)


class SupportResourceForm(forms.ModelForm):
    class Meta:
        model  = SupportResource
        fields = '__all__'
        labels = {
            'reading_assistance' : 'Lestraraðstoð',
            'interpretation': 'Túlkun fyrirmæla',
            'longer_time': 'Lengdur próftími',
        }


class ExceptionsForm(forms.ModelForm):

    class Meta:
        model  = Exceptions
        fields = '__all__'
        labels = {
            'student'   : 'Nemandi',
            'exempt'    : 'Virkja undanþágu',
            'signature' : 'Undirskrift',
            'date'      : 'Dagsetning',
        }


SupportResourceFormSet = forms.formset_factory(SupportResourceForm)
