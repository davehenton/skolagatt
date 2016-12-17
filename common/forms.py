from django                     import forms
from kennitala import Kennitala
from django.contrib.auth.models import User
from common.models import (
    Manager, Teacher, Student,
    School, StudentGroup, GroupSurvey,
    SurveyResult, SurveyLogin)


class ManagerForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ManagerForm, self).__init__(*args, **kwargs)
        self.fields['name'].widget.attrs.update({'class': 'form-control input-lg'})
        self.fields['ssn'].widget.attrs.update({'class': 'form-control input-lg'})
        self.fields['position'].widget.attrs.update({'class': 'form-control input-lg'})
        self.fields['email'].widget.attrs.update({'class': 'form-control input-lg'})
        self.fields['phone'].widget.attrs.update({'class': 'form-control input-lg'})

    def clean(self):
        cleaned_data = super(ManagerForm, self).clean()
        kt = Kennitala(cleaned_data.get('ssn'))
        if not kt.validate() or not kt.is_personal(cleaned_data.get('ssn')):
            raise forms.ValidationError(
                {"ssn": "Kennitala ekki rétt slegin inn"}
            )

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


class TeacherForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(TeacherForm, self).__init__(*args, **kwargs)
        self.fields['name'].widget.attrs.update({'class': 'form-control input-lg'})
        self.fields['ssn'].widget.attrs.update({'class': 'form-control input-lg'})
        self.fields['position'].widget.attrs.update({'class': 'form-control input-lg'})

    def clean(self):
        cleaned_data = super(TeacherForm, self).clean()
        kt = Kennitala(cleaned_data.get('ssn'))
        if not kt.validate() or not kt.is_personal(cleaned_data.get('ssn')):
            raise forms.ValidationError(
                {"ssn": "Kennitala ekki rétt slegin inn"}
            )

    class Meta:
        model = Teacher
        fields =  ['ssn', 'name', 'position', 'user']
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


class StudentForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(StudentForm, self).__init__(*args, **kwargs)
        self.fields['name'].widget.attrs.update({'class': 'form-control input-lg'})
        self.fields['ssn'].widget.attrs.update({'class': 'form-control input-lg'})

    def clean(self):
        cleaned_data = super(StudentForm, self).clean()
        kt = Kennitala(cleaned_data.get('ssn'))
        if not kt.validate() or not kt.is_personal(cleaned_data.get('ssn')):
            self.fields['ssn'].error_messages = 'Kennitala ekki rétt'
            raise forms.ValidationError(
                {"ssn": "Kennitala ekki rétt slegin inn"}
            )

    class Meta:
        model = Student
        fields =  ['ssn', 'name']
        labels = {
            'ssn': 'Kennitala',
            'name': 'Nafn',
        }
        error_messages = {
            'name': {
                'required': 'Verður að fylla út nafn'
            }
        }


class SchoolForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(SchoolForm, self).__init__(*args, **kwargs)
        self.fields['name'].widget.attrs.update({'class': 'form-control input-lg'})
        self.fields['ssn'].widget.attrs.update({'class': 'form-control input-lg'})
        self.fields['managers'].widget.attrs.update(
            {
                'class': 'form-control input-lg col-md-6 col-xs-12',
                'size' : '4'
            }
        )
        self.fields['teachers'].widget.attrs.update(
            {
                'class': 'form-control input-lg col-md-6 col-xs-12',
                'size' : '6'
            }
        )
        self.fields['students'].widget.attrs.update(
            {
                'class': 'form-control input-lg col-md-6 col-xs-12',
                'size' : '12'
            }
        )

    def clean(self):
        cleaned_data = super(SchoolForm, self).clean()
        kt = Kennitala(cleaned_data.get('ssn'))
        if not kt.validate() or kt.is_personal(cleaned_data.get('ssn')):
            raise forms.ValidationError(
                {"ssn": "Kennitala ekki rétt slegin inn"}
            )

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
        }


class StudentGroupForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(StudentGroupForm, self).__init__(*args, **kwargs)
        self.fields['name'].widget.attrs.update({'class': 'form-control input-lg'})
        self.fields['student_year'].widget.attrs.update({'class': 'form-control input-lg'})

    class Meta:
        model = StudentGroup
        fields =  ['name', 'student_year', 'group_managers', 'school', 'students']
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
        fields =  ['studentgroup', 'survey']
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


class SuperUserForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(SuperUserForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'form-control input-lg'})

    def clean(self):
        cleaned_data = super(SuperUserForm, self).clean()
        kt = Kennitala(cleaned_data.get('username'))
        if not kt.validate() or not kt.is_personal(cleaned_data.get('username')):
            raise forms.ValidationError(
                {"ssn": "Kennitala ekki rétt slegin inn"}
            )

    class Meta:
        model = User
        fields = ['username', 'is_superuser']
        labels = {
            'username': 'Kennitala',
            'is_superuser': 'Umsjónarmaður',
        }
