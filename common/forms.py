# -*- coding: utf-8 -*-
from django import forms
from kennitala import Kennitala
from django.contrib.auth.models import User
from common.models import (
    Manager, Teacher, Student,
    School, StudentGroup, GroupSurvey,
    SurveyResult, SurveyLogin, Notification,
    ExampleSurveyQuestion, ExampleSurveyAnswer,
)
from common.util import add_field_classes


class NotificationForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(NotificationForm, self).__init__(*args, **kwargs)
        add_field_classes(self, self.fields)

    class Meta:
        model = Notification
        fields = ['notification_type', 'notification_id']
        widgets = {'user': forms.HiddenInput()}


class FormWithSsnField(forms.ModelForm):
    person = True

    def _validate_ssn(self, key):
        ssn = self.cleaned_data.get(key)
        kt = Kennitala(ssn)
        if kt.validate():
            if self.person:
                if kt.is_personal(ssn):
                    return True
            else:
                if not kt.is_personal(ssn):
                    return True

        self.errors[key] = ['Kennitala ekki rétt slegin inn']
        return False

    def is_valid(self):
        valid_ret = super(FormWithSsnField, self).is_valid()

        if 'ssn' in self.cleaned_data:
            if not self._validate_ssn('ssn'):
                return False
        elif 'username' in self.cleaned_data:
            if not self._validate_ssn('username'):
                return False

        return valid_ret


class ManagerForm(FormWithSsnField):
    def __init__(self, *args, **kwargs):
        super(ManagerForm, self).__init__(*args, **kwargs)
        add_field_classes(self, self.fields)

    class Meta:
        model = Manager
        fields = ['ssn', 'name', 'email', 'phone', 'position', 'user']
        widgets = {'user': forms.HiddenInput()}
        labels = {
            'ssn': 'Kennitala',
            'name': 'Nafn',
            'email': 'Tölvupóstfang',
            'phone': 'Símanúmer',
            'position': 'Staða',
            'user': 'Notendur',
        }
        error_messages = {
            'name': {
                'required': 'Verður að fylla út nafn'
            }
        }


class TeacherForm(FormWithSsnField):
    def __init__(self, *args, **kwargs):
        super(TeacherForm, self).__init__(*args, **kwargs)
        add_field_classes(self, self.fields)

    class Meta:
        model = Teacher
        fields = ['ssn', 'name', 'position', 'user']
        widgets = {'user': forms.HiddenInput()}
        labels = {
            'ssn': 'Kennitala',
            'name': 'Nafn',
            'position': 'Staða',
            'user': 'Notendur',
        }
        error_messages = {
            'name': {
                'required': 'Verður að fylla út nafn'
            }
        }


class StudentForm(FormWithSsnField):
    def __init__(self, *args, **kwargs):
        super(StudentForm, self).__init__(*args, **kwargs)
        add_field_classes(self, self.fields)

    class Meta:
        model = Student
        fields = ['ssn', 'name']
        labels = {
            'ssn': 'Kennitala',
            'name': 'Nafn',
        }
        error_messages = {
            'name': {
                'required': 'Verður að fylla út nafn'
            }
        }


class SchoolForm(FormWithSsnField):
    person = False

    def __init__(self, *args, **kwargs):
        super(SchoolForm, self).__init__(*args, **kwargs)
        fields_to_update = ['name', 'ssn', 'school_nr', 'address', 'post_code', 'municipality', 'part']
        add_field_classes(self, fields_to_update)
        add_field_classes(self, ['managers', 'teachers', 'students'], cssdef={
            'class': 'form-control input-lg col-md-6 col-xs-12',
        })
        self.fields['managers'].widget.attrs.update({'size': 4})
        self.fields['teachers'].widget.attrs.update({'size': 6})
        self.fields['students'].widget.attrs.update({'size': 12})

    class Meta:
        model = School
        fields = '__all__'
        widgets = {'group': forms.HiddenInput()}
        labels = {
            'name': 'Nafn',
            'ssn': 'Kennitala',
            'managers': 'Stjórnendur',
            'teachers': 'Kennarar',
            'students': 'Nemendur',
            'school_nr': 'Skólanúmer',
            'address': 'Heimilisfang',
            'post_code': 'Póstnúmer',
            'municipality': 'Sveitarfélag',
            'part': 'Landshluti',
        }


class StudentGroupForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(StudentGroupForm, self).__init__(*args, **kwargs)
        add_field_classes(self, self.fields)

    class Meta:
        model = StudentGroup
        fields = ['name', 'student_year', 'group_managers', 'school', 'students']
        widgets = {'school': forms.HiddenInput()}
        labels = {
            'name': 'Nafn',
            'student_year': 'Árgangur',
            'group_managers': 'Kennarar',
            'school': 'Skóli',
            'students': 'Nemendur',
        }


class SurveyForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(SurveyForm, self).__init__(*args, **kwargs)
        self.fields['survey'].widget.attrs.update({'class': 'form-control'})

    class Meta:
        model = GroupSurvey
        fields = ['studentgroup', 'survey']
        widgets = {
            'studentgroup': forms.HiddenInput()
        }
        labels = {
            'studentgroup': 'Nemendahópur',
            'survey': 'Könnun',
        }


class SurveyResultForm(forms.ModelForm):
    class Meta:
        model = SurveyResult
        fields = []
        labels = {
            'student': 'Nemandi',
            'created_at': 'Búið til',
            'results': 'Niðurstöður',
            'reported_by': 'Skýrsla frá',
            'survey': 'Könnun',
        }


class SurveyLoginForm(forms.ModelForm):
    file = forms.FileField()

    class Meta:
        model = SurveyLogin
        fields = ['student', 'survey_id', 'survey_code']
        labels = {
            'student': 'Nemandi',
            'survey_id': 'Könnunarnúmer',
            'survey_code': 'Könnunarkóði',
        }


class SuperUserForm(FormWithSsnField):
    def __init__(self, *args, **kwargs):
        super(SuperUserForm, self).__init__(*args, **kwargs)
        add_field_classes(self, ['username'])

    class Meta:
        model = User
        fields = ['username', 'is_superuser']
        labels = {
            'username': 'Kennitala',
            'is_superuser': 'Umsjónarmaður',
        }


class ExampleSurveyQuestionForm(forms.ModelForm):
    class Meta:
        model = ExampleSurveyQuestion
        fields = [
            'quickcode',
            'quiz_type',
            'category',
            'description',
            'example',
        ]
        labels = {
            'quickcode': 'Flýtikóði',
            'quiz_type': 'Próftegund',
            'category': 'Spurningaflokkur',
            'description': 'Lýsing',
            'example': 'Dæmi',
        }


class ExampleSurveyAnswerForm(forms.ModelForm):
    file = forms.FileField()

    class Meta:
        model = ExampleSurveyAnswer
        fields = [
            'student',
            'question',
            'groupsurvey',
            'answer',
        ]
        labels = {
            'student': 'Nemandi',
            'question': 'Prófadæmis spurning',
            'groupsurvey': 'Próf',
            'answer': 'Svar',
        }
