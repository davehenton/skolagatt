# -*- coding: utf-8 -*-
from django.http                  import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts             import render, get_object_or_404, redirect
from django.views.generic         import ListView, CreateView, DetailView, UpdateView, DeleteView
from django.core.urlresolvers     import reverse_lazy
from django.contrib.auth.mixins   import UserPassesTestMixin
from django.contrib.auth.models   import User
from django.utils                 import timezone
from django.utils.decorators      import method_decorator
from django.views.decorators.csrf import csrf_exempt

from uuid      import uuid4
from datetime  import datetime, date
from ast       import literal_eval

import json
import xlrd
import openpyxl
from openpyxl.styles import PatternFill
from openpyxl.chart import AreaChart, BarChart, LineChart,  Reference
from openpyxl.chart.layout import Layout, ManualLayout

import csv

import common.mixins as common_mixins
from common.models import (
    Notification, School, Manager, Teacher, Student,
    StudentGroup, GroupSurvey, SurveyResult, SurveyLogin
)
import common.util   as common_util
import common.forms  as cm_forms
from survey.models import (
    Survey, SurveyGradingTemplate, SurveyInputField,
    SurveyInputGroup, SurveyResource, SurveyTransformation,
    SurveyType
)

from supportandexception.models import (
    SupportResource)

import supportandexception.models as sae_models


def lesferill(request):
    return render(request, 'common/lesferill.html')


class NotificationCreate(UserPassesTestMixin, CreateView):
    model = Notification
    form_class  = cm_forms.NotificationForm

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(NotificationCreate, self).dispatch(request, *args, **kwargs)

    def test_func(self):
        return self.request.user.is_authenticated

    def post(self, *args, **kwargs):
        try:
            notification_type = self.request.POST.get('notification_type', None)
            notification_id   = self.request.POST.get('notification_id', None)

            if notification_type and notification_id:
                Notification.objects.create(
                    user              = self.request.user,
                    notification_type = notification_type,
                    notification_id   = notification_id)

            return JsonResponse({'result': 'success'})
        except Exception as e:
            return JsonResponse({'result': 'error'})


class SchoolListing(ListView):
    model = School

    def get_context_data(self, **kwargs):
        context = super(SchoolListing, self).get_context_data(**kwargs)
        try:
            if self.request.user.is_superuser:
                context['school_list'] = common_util.slug_sort(
                    School.objects.all(), 'name')
            else:
                manager_schools        = School.objects.filter(
                    managers=Manager.objects.filter(user=self.request.user))
                teacher_schools        = School.objects.filter(
                    teachers=Teacher.objects.filter(user=self.request.user))
                context['school_list'] = list(
                    set(common_util.slug_sort(manager_schools | teacher_schools, 'name')))
        except Exception as e:
            pass
        return context


class SchoolDetail(common_mixins.SchoolEmployeeMixin, DetailView):
    model = School

    def get_context_data(self, **kwargs):
        context                      = super(SchoolDetail, self).get_context_data(**kwargs)
        context['studentgroup_list'] = common_util.slug_sort(
            self.object.studentgroup_set.all(), 'name')
        context['managers']          = common_util.slug_sort(
            self.object.managers.all(), 'name')
        context['teachers']          = common_util.slug_sort(
            self.object.teachers.all(), 'name')
        context['surveys']           = common_util.slug_sort(
            GroupSurvey.objects.filter(
                studentgroup__in=self.object.studentgroup_set.all()), 'survey')
        context['students']          = self.object.students.all()

        all_messages = common_util.get_messages()
        messages     = []
        for message in all_messages:
            if message['file'] is not None:
                file_name            = message['file'].split('/')[-1]
                file_name            = file_name.encode('utf-8')
                message['file_name'] = file_name
            messages.append(message)

        if common_util.is_school_teacher(self.request, self.kwargs):
            context['messages'] = [
                message for message in messages if message['teachers_allow'] is True
            ]
        else:
            context['messages'] = messages

        return context


class SchoolCreate(common_mixins.SuperUserMixin, CreateView):
    model       = School
    form_class  = cm_forms.SchoolForm
    success_url = reverse_lazy('schools:school_listing')


class SchoolCreateImport(common_mixins.SchoolManagerMixin, CreateView):
    model         = School
    form_class    = cm_forms.SchoolForm
    template_name = "common/school_form_import.html"

    def get_context_data(self, **kwargs):
        # xxx will be available in the template as the related objects
        context = super(SchoolCreateImport, self).get_context_data(**kwargs)
        return context

    def post(self, *args, **kwargs):
        if(self.request.FILES):
            u_file    = self.request.FILES['file'].name
            extension = u_file.split(".")[-1]
            ssn       = self.request.POST.get('school_ssn')
            name      = self.request.POST.get('school_name')
            title     = self.request.POST.get('title')
            if title == 'yes':
                first = 1
            else:
                first = 0
            data = []
            if extension == 'csv':
                for row in self.request.FILES['file'].readlines()[first:]:
                    row         = row.decode('utf-8')
                    school_ssn  = row.split(',')[int(ssn)]
                    school_name = row.split(',')[int(name)]
                    data.append({'name': school_name.strip(), 'ssn': school_ssn.strip()})
            elif extension == 'xlsx':
                input_excel = self.request.FILES['file']
                book        = xlrd.open_workbook(file_contents=input_excel.read())
                for sheetsnumber in range(book.nsheets):
                    sheet = book.sheet_by_index(sheetsnumber)
                    for row in range(first, sheet.nrows):
                        data.append({
                            'name': sheet.cell_value(row, int(name)),
                            'ssn' : str(int(sheet.cell_value(row, int(ssn))))})

            return render(self.request, 'common/school_verify_import.html', {'data': data})
        else:
            school_data = json.loads(self.request.POST['schools'])
            # iterate through students, add them if they don't exist then add to school
            for school in school_data:
                try:
                    School.objects.create(**school)
                except:
                    pass  # student already exists

        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
            return reverse_lazy('schools:school_listing')


class SchoolUpdate(common_mixins.SuperUserMixin, UpdateView):
    model       = School
    form_class  = cm_forms.SchoolForm
    success_url = reverse_lazy('schools:school_listing')


class SchoolDelete(common_mixins.SuperUserMixin, DeleteView):
    model         = School
    template_name = "schools/confirm_delete.html"
    success_url   = reverse_lazy('schools:school_listing')


class ManagerListing(common_mixins.SchoolEmployeeMixin, ListView):
    model = Manager

    def get_context_data(self, **kwargs):
        context             = super(ManagerListing, self).get_context_data(**kwargs)
        school              = School.objects.get(pk=self.kwargs['school_id'])
        context['school']   = school
        context['managers'] = Manager.objects.filter(school=school)
        return context


class ManagerDetail(common_mixins.SchoolEmployeeMixin, DetailView):
    model = Manager

    def get_context_data(self, **kwargs):
        context           = super(ManagerDetail, self).get_context_data(**kwargs)
        context['school'] = School.objects.get(pk=self.kwargs['school_id'])
        return context


class ManagerOverview(UserPassesTestMixin, DetailView):
    model = Manager

    def test_func(self):
        try:
            if self.request.user.id == Manager.objects.get(pk=self.kwargs['pk']).user.id:
                return True
        except:
            return False
        return False

    def get_context_data(self, **kwargs):
        context           = super(ManagerOverview, self).get_context_data(**kwargs)
        context['school'] = School.objects.filter(
            managers=Manager.objects.filter(
                pk=self.kwargs['pk'])).first()
        return context


class ManagerCreate(common_mixins.SchoolManagerMixin, CreateView):
    model      = Manager
    form_class = cm_forms.ManagerForm

    def get_context_data(self, **kwargs):
        context           = super(ManagerCreate, self).get_context_data(**kwargs)
        context['school'] = School.objects.get(pk=self.kwargs['school_id'])
        return context

    def post(self, *args, **kwargs):
        self.object = Manager.objects.filter(
            user__username=self.request.POST.get('ssn')).first()
        if self.object:
            return HttpResponseRedirect(self.get_success_url())
        form      = self.get_form()
        # make data mutable
        form.data = self.request.POST.copy()
        # set or create user
        user      = User.objects.filter(username=self.request.POST.get('ssn'))
        if user:
            form.data['user'] = user.first().id
        else:
            new_user = User.objects.create(
                username = self.request.POST.get('ssn'),
                password = str(uuid4()))
            form.data['user'] = new_user.id
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def get_success_url(self):
        try:
            school_id = self.kwargs['school_id']
            # Try getting the School object. If it doesn't exist it should return an error
            School.objects.get(pk=school_id).managers.add(self.object)
            return reverse_lazy(
                'schools:school_detail',
                kwargs={'pk': school_id})
        except:
            return reverse_lazy('schools:school_listing')

    def get_initial(self):
        school = get_object_or_404(School, pk=self.kwargs.get('school_id'))
        return {
            'school': school,
        }


class ManagerCreateImport(common_mixins.SchoolManagerMixin, CreateView):
    model         = School
    form_class    = cm_forms.SchoolForm
    template_name = "common/manager_form_import.html"

    def get_context_data(self, **kwargs):
        # xxx will be available in the template as the related objects
        context = super(ManagerCreateImport, self).get_context_data(**kwargs)
        return context

    def post(self, *args, **kwargs):
        if(self.request.FILES):
            u_file     = self.request.FILES['file'].name
            extension  = u_file.split(".")[-1]
            ssn        = self.request.POST.get('ssn')
            name       = self.request.POST.get('name')
            school_ssn = self.request.POST.get('school_ssn')
            title      = self.request.POST.get('title')
            if title == 'yes':
                first = 1
            else:
                first = 0
            data = []
            if extension == 'csv':
                for row in self.request.FILES['file'].readlines()[first:]:
                    row        = row.decode('utf-8')
                    school_ssn = row.split(',')[int(school_ssn)]
                    ssn        = row.split(',')[ssn]
                    name       = row.split(',')[name]
                    data.append({
                        'name'      : name.strip(),
                        'ssn'       : ssn.strip(),
                        'school_ssn': school_ssn.strip()
                    })
            elif extension == 'xlsx':
                input_excel = self.request.FILES['file']
                book        = xlrd.open_workbook(file_contents=input_excel.read())
                for sheetsnumber in range(book.nsheets):
                    sheet = book.sheet_by_index(sheetsnumber)
                    for row in range(first, sheet.nrows):
                        data.append({
                            'name'      : sheet.cell_value(row, int(name)),
                            'ssn'       : str(int(sheet.cell_value(row, int(ssn)))),
                            'school_ssn': str(int(sheet.cell_value(row, int(school_ssn))))
                        })

            return render(self.request, 'common/manager_verify_import.html', {'data': data})
        else:
            manager_data = json.loads(self.request.POST['managers'])
            # iterate through managers, add them if they don't exist then add to school
            for manager in manager_data:
                try:
                    School.objects.get(
                        ssn=manager['school_ssn']
                    ).managers.add(**manager)
                except:
                    pass  # manager already exists

        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
            return reverse_lazy('schools:school_listing')


class ManagerUpdate(common_mixins.SchoolManagerMixin, UpdateView):
    model      = Manager
    form_class = cm_forms.ManagerForm

    def get_context_data(self, **kwargs):
        context           = super(ManagerUpdate, self).get_context_data(**kwargs)
        context['school'] = School.objects.get(pk=self.kwargs['school_id'])
        return context

    def post(self, request, **kwargs):
        # get Manager to be updated
        self.object = Manager.objects.get(pk=self.kwargs['pk'])
        # get user by ssn
        try:
            user = User.objects.get(username=self.request.POST.get('ssn'))
        except:
            user = User.objects.create(username=self.request.POST.get('ssn'), password=str(uuid4()))

        if self.object.user == user:
            # no changes
            pass
        else:
            request.POST         = request.POST.copy()
            request.POST['user'] = user.id

        return super(ManagerUpdate, self).post(request, **kwargs)

    def get_success_url(self):
        try:
            school_id = self.kwargs['school_id']
            return reverse_lazy(
                'schools:school_detail',
                kwargs={'pk': school_id}
            )
        except:
            return reverse_lazy('schools:school_listing')


class ManagerDelete(common_mixins.SchoolManagerMixin, DeleteView):
    model         = Manager
    template_name = "schools/confirm_delete.html"

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        # delete manager_school entry
        School.objects.get(
            pk=self.kwargs.get('school_id')
        ).managers.remove(self.object)
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        try:
            return reverse_lazy(
                'schools:school_detail',
                kwargs={'pk': self.kwargs['school_id']}
            )
        except:
            return reverse_lazy('schools:school_listing')


class TeacherListing(common_mixins.SchoolEmployeeMixin, ListView):
    model = Teacher

    def get_context_data(self, **kwargs):
        context             = super(TeacherListing, self).get_context_data(**kwargs)
        school              = School.objects.get(pk=self.kwargs['school_id'])
        context['school']   = school
        context['teachers'] = Teacher.objects.filter(school=school)
        context['groups']   = common_util.slug_sort(
            StudentGroup.objects.filter(school=school), 'name')
        return context


class TeacherDetail(common_mixins.SchoolEmployeeMixin, DetailView):
    model = Teacher

    def get_context_data(self, **kwargs):
        context           = super(TeacherDetail, self).get_context_data(**kwargs)
        context['school'] = School.objects.get(pk=self.kwargs['school_id'])
        context['groups'] = common_util.slug_sort(
            StudentGroup.objects.filter(
                group_managers = Teacher.objects.filter(
                    user = self.request.user)
            ), 'name'
        )
        return context


class TeacherOverview(UserPassesTestMixin, DetailView):
    model = Teacher

    def test_func(self):
        try:
            if self.request.user.id == Teacher.objects.get(
                pk=self.kwargs['pk']
            ).user.id:
                return True
        except:
            return False
        return False

    def get_context_data(self, **kwargs):
        context           = super(TeacherOverview, self).get_context_data(**kwargs)
        context['school'] = School.objects.filter(
            teachers=Teacher.objects.filter(
                pk=self.kwargs['pk']
            )
        ).first()
        return context


class TeacherCreate(common_mixins.SchoolManagerMixin, CreateView):
    model      = Teacher
    form_class = cm_forms.TeacherForm

    def get_context_data(self, **kwargs):
        context           = super(TeacherCreate, self).get_context_data(**kwargs)
        context['school'] = School.objects.get(pk=self.kwargs['school_id'])
        return context

    def post(self, *args, **kwargs):
        self.object = Teacher.objects.filter(
            ssn=self.request.POST.get('ssn')
        ).first()
        if self.object:
            return HttpResponseRedirect(self.get_success_url())
        form      = self.get_form()
        # make data mutable
        form.data = self.request.POST.copy()
        # set or create user
        user      = User.objects.filter(username=self.request.POST.get('ssn'))

        if user:
            form.data['user'] = user.first().id
        else:
            user = User.objects.create(
                username = self.request.POST.get('ssn'),
                password = str(uuid4()))
            form.data['user'] = user.id

        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def get_success_url(self):
        try:
            school_id = self.kwargs['school_id']
            School.objects.get(pk=school_id).teachers.add(self.object)
            return reverse_lazy(
                'schools:school_detail',
                kwargs={'pk': school_id}
            )
        except:
            return reverse_lazy('schools:school_listing')


class TeacherCreateImport(common_mixins.SchoolManagerMixin, CreateView):
    model         = Teacher
    form_class    = cm_forms.TeacherForm
    template_name = "common/teacher_form_import.html"

    def get_context_data(self, **kwargs):
        # xxx will be available in the template as the related objects
        context           = super(TeacherCreateImport, self).get_context_data(**kwargs)
        context['school'] = School.objects.get(pk=self.kwargs['school_id'])
        return context

    def post(self, *args, **kwargs):
        if(self.request.FILES):
            u_file    = self.request.FILES['file'].name
            extension = u_file.split(".")[-1]
            ssn       = self.request.POST.get('ssn')
            name      = self.request.POST.get('name')
            title     = self.request.POST.get('title')
            if title == 'yes':
                first = 1
            else:
                first = 0
            data = []
            if extension == 'csv':
                for row in self.request.FILES['file'].readlines()[first:]:
                    row  = row.decode('utf-8')
                    ssn  = row.split(',')[ssn]
                    name = row.split(',')[name]
                    data.append({
                        'name': name.strip(),
                        'ssn' : ssn.strip().zfill(10),
                    })
            elif extension == 'xlsx':
                input_excel = self.request.FILES['file']
                book        = xlrd.open_workbook(file_contents=input_excel.read())
                for sheetsnumber in range(book.nsheets):
                    sheet = book.sheet_by_index(sheetsnumber)
                    for row in range(first, sheet.nrows):
                        if str(sheet.cell_value(row, int(ssn)))[0].isspace():
                            data.append({
                                'name': str(sheet.cell_value(row, int(name))),
                                'ssn' : str(sheet.cell_value(row, int(ssn)))[1:].zfill(10)
                            })
                        elif isinstance(sheet.cell_value(row, int(ssn)), float):
                            data.append({
                                'name': str(sheet.cell_value(row, int(name))),
                                'ssn' : str(int(sheet.cell_value(row, int(ssn)))).zfill(10)
                            })
                        else:
                            data.append({
                                'name': str(sheet.cell_value(row, int(name))),
                                'ssn' : str(sheet.cell_value(row, int(ssn))).zfill(10)
                            })

            return render(
                self.request,
                'common/teacher_verify_import.html',
                {
                    'data': data,
                    'school': School.objects.get(pk=self.kwargs['school_id'])
                }
            )
        else:
            teacher_data = json.loads(self.request.POST['teachers'])
            # iterate through teachers, add them if they don't exist then add to school
            for teacher in teacher_data:
                try:
                    u, c = User.objects.get_or_create(username=teacher['ssn'])
                    t, c = Teacher.objects.get_or_create(
                        ssn=teacher['ssn'], name=teacher['name'], user=u)
                    School.objects.get(pk=self.kwargs['school_id']).teachers.add(t)
                except Exception as e:
                    pass  # teacher already exists
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        try:
            return reverse_lazy(
                'schools:school_detail',
                kwargs={'pk': self.kwargs['school_id']}
            )
        except:
            return reverse_lazy('schools:school_listing')


class TeacherUpdate(common_mixins.SchoolManagerMixin, UpdateView):
    model      = Teacher
    form_class = cm_forms.TeacherForm

    def get_context_data(self, **kwargs):
        context           = super(TeacherUpdate, self).get_context_data(**kwargs)
        context['school'] = School.objects.get(pk=self.kwargs['school_id'])
        return context

    def post(self, request, **kwargs):
        # get Teacher to be updated
        self.object = Teacher.objects.get(pk=self.kwargs['pk'])
        # get user by ssn
        try:
            user = User.objects.get(username=self.request.POST.get('ssn'))
        except:
            user = User.objects.create(username=self.request.POST.get('ssn'), password=str(uuid4()))

        if self.object.user == user:
            # no changes
            pass
        else:
            request.POST         = request.POST.copy()
            request.POST['user'] = user.id

        return super(TeacherUpdate, self).post(request, **kwargs)

    def get_success_url(self):
        try:
            school_id = self.kwargs['school_id']
            return reverse_lazy(
                'schools:school_detail',
                kwargs={'pk': school_id}
            )
        except:
            return reverse_lazy('schools:school_listing')


class TeacherDelete(common_mixins.SchoolManagerMixin, DeleteView):
    model         = Teacher
    template_name = "schools/confirm_delete.html"

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        # delete teacher_school entry
        School.objects.get(
            pk=self.kwargs.get('school_id')
        ).teachers.remove(self.object)
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        try:
            return reverse_lazy(
                'schools:school_detail',
                kwargs={'pk': self.kwargs['school_id']}
            )
        except:
            return reverse_lazy('schools:school_listing')


class StudentListing(common_mixins.SchoolEmployeeMixin, ListView):
    model = Student

    def get_context_data(self, **kwargs):
        context = super(StudentListing, self).get_context_data(**kwargs)
        school  = School.objects.get(pk=self.kwargs['school_id'])

        context['school']   = school
        context['students'] = common_util.slug_sort(
            Student.objects.filter(school=school), 'name')
        context['students_outside_groups'] = common_util.slug_sort(
            Student.objects.filter(school=school).exclude(
                studentgroup__in=StudentGroup.objects.filter(school=school)
            ), 'name')
        return context


class StudentDetail(common_mixins.SchoolEmployeeMixin, DetailView):
    model = Student

    def get_context_data(self, **kwargs):
        # xxx will be available in the template as the related objects
        context                     = super(StudentDetail, self).get_context_data(**kwargs)
        context['school']           = School.objects.get(pk=self.kwargs['school_id'])
        context['student_moreinfo'] = sae_models.StudentExceptionSupport.objects.filter(
            student=self.kwargs.get('pk')).get
        return context


def StudentNotes(request, school_id, pk):
    if request.method == 'POST':
        notes = request.POST.get('notes')
        if (sae_models.StudentExceptionSupport.objects.filter(
            student = Student.objects.get(pk=int(pk))
        ).exists()):
            sae_models.StudentExceptionSupport.objects.filter(
                student = Student.objects.get(pk=int(pk))).update(notes=notes)
        else:
            ses         = sae_models.StudentExceptionSupport(notes=notes)
            ses.student = Student.objects.get(pk=int(pk))
            ses.save()
        return JsonResponse({"message": "success"})


class StudentCreateImport(common_mixins.SchoolManagerMixin, CreateView):
    model         = Student
    form_class    = cm_forms.StudentForm
    template_name = "common/student_form_import.html"

    def get_context_data(self, **kwargs):
        # xxx will be available in the template as the related objects
        context           = super(StudentCreateImport, self).get_context_data(**kwargs)
        context['school'] = School.objects.get(pk=self.kwargs['school_id'])
        return context

    def post(self, *args, **kwargs):
        if(self.request.FILES):
            u_file    = self.request.FILES['file'].name
            extension = u_file.split(".")[-1]
            ssn       = self.request.POST.get('student_ssn')
            name      = self.request.POST.get('student_name')
            title     = self.request.POST.get('title')
            if title == 'yes':
                first = 1
            else:
                first = 0
            data = []
            if extension == 'csv':
                for row in self.request.FILES['file'].readlines()[first:]:
                    row          = row.decode('utf-8')
                    student_ssn  = row.split(',')[int(ssn)]
                    student_name = row.split(',')[int(name)]
                    if len(student_ssn.strip()) == 10:
                        data.append({
                            'name': student_name.strip(),
                            'ssn': student_ssn.strip().zfill(10)
                        })
                    else:
                        return render(self.request, 'common/student_error_import.html')
            elif extension == 'xlsx':
                input_excel = self.request.FILES['file']
                book        = xlrd.open_workbook(file_contents=input_excel.read())
                for sheetsnumber in range(book.nsheets):
                    sheet = book.sheet_by_index(sheetsnumber)
                    for row in range(first, sheet.nrows):
                        if len(str(sheet.cell_value(row, int(ssn))).strip()) == 10:
                            data.append({
                                'name': str(sheet.cell_value(row, int(name))).strip(),
                                'ssn' : str(sheet.cell_value(row, int(ssn))).strip().zfill(10)
                            })
                        else:
                            return render(self.request, 'common/student_error_import.html')
            return render(
                self.request,
                'common/student_verify_import.html',
                {
                    'data': data,
                    'school': School.objects.get(pk=self.kwargs['school_id'])
                }
            )
        else:
            student_data = json.loads(self.request.POST['students'])
            school       = School.objects.get(pk=self.kwargs['school_id'])
            # iterate through students, add them if they don't exist then add to school
            for data in student_data:
                student = None
                try:
                    student = Student.objects.create(**data)
                except:
                    student = Student.objects.get(ssn=data['ssn'])
                school.students.add(student)

        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        try:
            school_id = self.kwargs['school_id']
            School.objects.get(pk=school_id).students.add(self.object)
            return reverse_lazy(
                'schools:school_detail',
                kwargs={'pk': school_id}
            )
        except:
            return reverse_lazy('schools:school_listing')


class StudentCreate(common_mixins.SchoolManagerMixin, CreateView):
    model      = Student
    form_class = cm_forms.StudentForm

    def post(self, *args, **kwargs):
        self.object = Student.objects.filter(ssn=self.request.POST.get('ssn')).first()
        # if self.object:
        #     return HttpResponseRedirect(self.get_success_url())
        form = self.get_form()
        # make data mutable
        form.data = self.request.POST.copy()
        # set or create user
        user = User.objects.filter(username=self.request.POST.get('ssn'))
        if user:
            form.data['user'] = user
        else:
            form.data['user'] = User.objects.create(
                username=self.request.POST.get('ssn'),
                password=str(uuid4())
            )
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def get_context_data(self, **kwargs):
        context           = super(StudentCreate, self).get_context_data(**kwargs)
        context['school'] = School.objects.get(pk=self.kwargs['school_id'])
        return context

    def get_success_url(self):
        try:
            school_id = self.kwargs['school_id']
            School.objects.get(pk=school_id).students.add(self.object)
            return reverse_lazy(
                'schools:school_detail',
                kwargs={'pk': school_id}
            )
        except:
            return reverse_lazy('schools:school_listing')


class StudentUpdate(common_mixins.SchoolManagerMixin, UpdateView):
    model      = Student
    form_class = cm_forms.StudentForm

    def get_context_data(self, **kwargs):
        context           = super(StudentUpdate, self).get_context_data(**kwargs)
        context['school'] = School.objects.get(pk=self.kwargs['school_id'])
        return context

    def get_success_url(self):
        try:
            school_id = self.kwargs['school_id']
            return reverse_lazy(
                'schools:school_detail',
                kwargs={'pk': school_id}
            )
        except:
            return reverse_lazy('schools:school_listing')


class StudentDelete(common_mixins.SchoolManagerMixin, DeleteView):
    model         = Student
    template_name = "schools/confirm_delete.html"

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        # delete student_school entry
        School.objects.get(
            pk=self.kwargs.get('school_id')
        ).students.remove(self.object)
        # remove student from all studentgroups in school
        for group in StudentGroup.objects.filter(school=self.kwargs.get('school_id')):
            group.students.remove(self.object)
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        try:
            school_id = self.kwargs['school_id']
            return reverse_lazy(
                'schools:school_detail',
                kwargs={'pk': school_id}
            )
        except:
            return reverse_lazy('schools:school_listing')


class StudentGroupListing(common_mixins.SchoolEmployeeMixin, ListView):
    model = StudentGroup

    def get_context_data(self, **kwargs):
        context                  = super(StudentGroupListing, self).get_context_data(**kwargs)
        school                   = School.objects.get(pk=self.kwargs['school_id'])
        context['school']        = school
        context['studentgroups'] = common_util.slug_sort(
            StudentGroup.objects.filter(school=school), 'name')
        return context


class StudentGroupDetail(common_mixins.SchoolEmployeeMixin, DetailView):
    model = StudentGroup

    def get_context_data(self, **kwargs):
        # xxx will be available in the template as the related objects
        context                = super(StudentGroupDetail, self).get_context_data(**kwargs)
        context['school']      = School.objects.get(pk=self.kwargs['school_id'])
        context['exceptions']  = sae_models.Exceptions.objects.all()
        context['supports']    = sae_models.SupportResource.objects.all()
        context['surveys']     = self.object.groupsurvey_set.filter(
            active_to__gte=datetime.now()
        )
        context['old_surveys'] = self.object.groupsurvey_set.filter(
            active_to__lt=datetime.now()
        )
        context['students']    = common_util.slug_sort(self.object.students.all(), 'name')
        context['teachers']    = common_util.slug_sort(self.object.group_managers.all(), 'name')
        return context


def group_admin_listing_csv(request, survey_title):
        from ast import literal_eval
        # Create the HttpResponse object with the appropriate CSV header.
        response                        = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="' + survey_title + '.csv"'
        fieldnames = [
            'FIRST', 'LAST', 'RESULTS EMAIL', 'EXTERNAL ID',
            'CODE EMAIL', 'TEST NAME', 'GROUP PATH', 'EXTRA TIME'
        ]
        writer = csv.writer(response)
        writer.writerow(fieldnames)

        KEY = {
            1: 'íslenska',
            2: 'enska',
            3: 'stærðfræði'
        }

        surveys = GroupSurvey.objects.filter(title=survey_title)
        for survey in surveys:
            for student in survey.studentgroup.students.all():
                # find last name by finding last space
                student_names       = student.name.strip().split(" ")
                student_first_names = ' '.join(student_names[:-1])
                student_lastname    = student_names[-1]

                student_processed = False
                if student.supportresource_set.exists():
                    longer_time        = literal_eval(
                        student.supportresource_set.first().longer_time)
                    reading_assistance = literal_eval(
                        student.supportresource_set.first().reading_assistance)
                    """Fyrir öll stuðningsúrræði, ath hvort stuðningsúrræðið sé fyrir þetta próf"""
                    for i in longer_time + reading_assistance:
                        if KEY.get(i, '') in survey.identifier and not student_processed:
                            """
                                Próftaki með lengdan tíma og engan stuðning á að fá venjulegt
                                próf með lengdum tíma
                            """
                            if i in longer_time and i not in reading_assistance:
                                writer.writerow([
                                    student_first_names,
                                    student_lastname,
                                    '',
                                    student.ssn,
                                    '',
                                    survey.identifier,
                                    '',
                                    'Y'
                                ])
                            else:
                                """Annars lengdur tími og stuðningur"""
                                writer.writerow([
                                    student_first_names,
                                    student_lastname,
                                    '',
                                    student.ssn,
                                    '',
                                    survey.identifier + '_stuðningur',
                                    '',
                                    'Y'
                                ])
                            student_processed = True

                if not student_processed:
                    """Próftaki fær venjulegt próf"""
                    writer.writerow([
                        student_first_names,
                        student_lastname,
                        '',
                        student.ssn,
                        '',
                        survey.identifier,
                        '',
                        ''
                    ])

        return response


class StudentGroupAdminListing(common_mixins.SuperUserMixin, ListView):
    model         = StudentGroup
    template_name = "common/studentgroup_admin_list.html"

    def get_context_data(self, **kwargs):
        try:
            context            = super(StudentGroupAdminListing, self).get_context_data(**kwargs)
            context['schools'] = common_util.slug_sort(School.objects.all(), 'name')
            context['surveys'] = GroupSurvey.objects.filter(
                survey__title=self.kwargs['survey_title']
            )
        except Exception as e:
            context['error'] = str(e)
        return context


class StudentGroupCreate(common_mixins.SchoolEmployeeMixin, CreateView):
    model = StudentGroup
    form_class = cm_forms.StudentGroupForm

    def get_context_data(self, **kwargs):
        # xxx will be available in the template as the related objects
        context             = super(StudentGroupCreate, self).get_context_data(**kwargs)
        context['school']   = School.objects.get(pk=self.kwargs['school_id'])
        context['students'] = common_util.slug_sort(
            Student.objects.filter(school=self.kwargs['school_id']), 'name')
        context['teachers'] = common_util.slug_sort(
            Teacher.objects.filter(school=self.kwargs['school_id']), 'name')

        return context

    def post(self, request, *args, **kwargs):
        self.object         = None
        form                = self.get_form()
        # make data mutable
        form.data           = self.request.POST.copy()
        form.data['school'] = School.objects.get(pk=self.kwargs['school_id']).pk
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def get_success_url(self):
        try:
            school_id = self.kwargs['school_id']
            return reverse_lazy(
                'schools:school_detail',
                kwargs={'pk': school_id}
            )
        except:
            return reverse_lazy('schools:school_listing')


class StudentGroupUpdate(common_mixins.SchoolEmployeeMixin, UpdateView):
    model      = StudentGroup
    form_class = cm_forms.StudentGroupForm

    def get_context_data(self, **kwargs):
        # xxx will be available in the template as the related objects
        context                   = super(StudentGroupUpdate, self).get_context_data(**kwargs)
        context['school']         = School.objects.get(pk=self.kwargs['school_id'])
        context['students']       = common_util.slug_sort(
            Student.objects.filter(school=self.kwargs['school_id']), 'name')
        context['teachers']       = common_util.slug_sort(
            Teacher.objects.filter(school=self.kwargs['school_id']), 'name')
        context['group_managers'] = Teacher.objects.filter(studentgroup=self.kwargs['pk'])
        return context

    def post(self, request, *args, **kwargs):
        self.object         = None
        form                = self.get_form()
        # make data mutable
        form.data           = self.request.POST.copy()
        form.data['school'] = School.objects.get(pk=self.kwargs['school_id']).pk
        form                = cm_forms.StudentGroupForm(
            form.data or None,
            instance = StudentGroup.objects.get(id=self.kwargs['pk'])
        )
        if form.is_valid():
            form.save()
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def get_success_url(self):
        try:
            school_id = self.kwargs['school_id']
            return reverse_lazy(
                'schools:group_detail',
                kwargs={'school_id': school_id, 'pk': self.kwargs['pk']}
            )
        except:
            return reverse_lazy('schools:school_listing')


class StudentGroupDelete(common_mixins.SchoolEmployeeMixin, DeleteView):
    model         = StudentGroup
    template_name = "schools/confirm_delete.html"

    def get_success_url(self):
        try:
            school_id = self.kwargs['school_id']
            return reverse_lazy(
                'schools:school_detail',
                kwargs={'pk': school_id}
            )
        except:
            return reverse_lazy('schools:school_listing')


class SurveyListing(common_mixins.SchoolEmployeeMixin, ListView):
    model = GroupSurvey

    def get_context_data(self, **kwargs):
        # xxx will be available in the template as the related objects
        context                 = super(SurveyListing, self).get_context_data(**kwargs)
        context['school']       = School.objects.get(pk=self.kwargs['school_id'])
        group                   = StudentGroup.objects.get(pk=self.kwargs['student_group'])
        context['studentgroup'] = group
        context['surveys']      = GroupSurvey.objects.filter(studentgroup = group)
        return context


class SurveyAdminListing(common_mixins.SuperUserMixin, ListView):
    model         = GroupSurvey
    template_name = "common/survey_admin_list.html"

    def get_context_data(self, **kwargs):
        # xxx will be available in the template as the related objects
        try:
            context            = super(SurveyAdminListing, self).get_context_data(**kwargs)
            context['surveys'] = Survey.objects.all()
        except Exception as e:
            context['error'] = str(e)
        return context


class SurveyDetail(common_mixins.SchoolEmployeeMixin, DetailView):
    model = GroupSurvey

    def get_context_data(self, **kwargs):
        # xxx will be available in the template as the related objects
        context = super(SurveyDetail, self).get_context_data(**kwargs)
        survey = Survey.objects.filter(pk=self.object.survey.id)[0]
        survey_type = SurveyType.objects.filter(survey=self.object.survey.id).values('id')
        dic = survey_type[0]
        survey_type = dic['id']
        context['survey_details']   = survey
        context['survey_resources'] = SurveyResource.objects.filter(survey=survey)
        context['school']           = School.objects.get(pk=self.kwargs['school_id'])
        context['studentgroup']     = StudentGroup.objects.get(pk=self.kwargs['student_group'])
        transformation = SurveyTransformation.objects.filter(survey=survey)
        if transformation == []:
            transformation = -1

        try:
            context['students'] = self.object.studentgroup.students.all()
            context['expired']  = True if self.object.survey.active_to < date.today() else False
        except:
            context['students'] = []
            context['expired']  = False
        student_results     = {}
        for student in context['students']:
            sr = SurveyResult.objects.filter(student=student, survey=self.object)
            print('edadfas')
            print(sr)
            if sr:
                r = literal_eval(sr.first().results)  # get student results
                try:
                    student_results[student] = common_util.calc_survey_results(
                        survey_identifier = self.object.survey.identifier,
                        click_values = literal_eval(r['click_values']),
                        input_values = r['input_values'],
                        student = student,
                        survey_type = survey_type,
                        transformation = transformation,
                    )
                except Exception as e:
                    student_results[student] = common_util.calc_survey_results(
                        survey_identifier = self.object.survey.identifier,
                        click_values = [],
                        input_values = r['input_values'],
                        student = student,
                        survey_type = survey_type,
                        transformation = transformation)

            else:
                student_results[student] = common_util.calc_survey_results(
                    survey_identifier = self.object.survey.identifier,
                    click_values = [],
                    input_values = {},
                    student = student,
                    survey_type = survey_type)
        context['student_results'] = student_results
        context['field_types']     = ['text', 'number', 'text-list', 'number-list']
        return context


class SurveyCreate(common_mixins.SchoolEmployeeMixin, CreateView):
    model      = GroupSurvey
    form_class = cm_forms.SurveyForm

    def get_form(self):
        form       = super(SurveyCreate, self).get_form(self.form_class)
        group_year = StudentGroup.objects.get(
            pk=self.kwargs['student_group']).student_year
        survey_set = Survey.objects.filter(student_year=group_year, active_to__gte=timezone.now().date())
        form.fields['survey'].queryset = survey_set
        return form

    def post(self, *args, **kwargs):
        self.object               = None
        form                      = self.get_form()
        # make data mutable
        form.data                 = self.request.POST.copy()
        form.data['studentgroup'] = StudentGroup.objects.filter(
            pk=self.kwargs['student_group'])
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def get_success_url(self):
        try:
            school_id     = self.kwargs['school_id']
            student_group = self.kwargs['student_group']
            return reverse_lazy(
                'schools:group_detail',
                kwargs={'school_id': school_id, 'pk': student_group}
            )
        except:
            return reverse_lazy('schools:school_listing')


class SurveyUpdate(common_mixins.SchoolEmployeeMixin, UpdateView):
    model      = GroupSurvey
    form_class = cm_forms.SurveyForm

    def get_form(self):
        form           = super(SurveyUpdate, self).get_form(self.form_class)
        group_year = StudentGroup.objects.get(
            pk=self.kwargs['student_group']).student_year

        survey_set                     = Survey.objects.filter(student_year=group_year)
        form.fields['survey'].queryset = survey_set
        return form

    def get_context_data(self, **kwargs):
            # xxx will be available in the template as the related objects
            context                = super(SurveyUpdate, self).get_context_data(**kwargs)
            try:
                context['survey_description'] = self.object.survey.description
            except:
                context['survey_description'] = "Veldu próf..."
            return context

    def get_success_url(self):
        try:
            school_id = self.kwargs['school_id']
            return reverse_lazy(
                'schools:school_detail',
                kwargs={'pk': school_id}
            )
        except:
            return reverse_lazy('schools:school_listing')


class SurveyDelete(common_mixins.SchoolEmployeeMixin, DeleteView):
    model         = GroupSurvey
    template_name = "schools/confirm_delete.html"

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        success_url = self.get_success_url()
        # delete SurveyResults
        SurveyResult.objects.filter(survey=self.object).delete()
        self.object.delete()
        return HttpResponseRedirect(success_url)

    def get_success_url(self):
        try:
            school_id = self.kwargs['school_id']
            return reverse_lazy(
                'schools:school_detail',
                kwargs={'pk': school_id}
            )
        except:
            return reverse_lazy('schools:school_listing')


class SurveyResultCreate(common_mixins.SchoolEmployeeMixin, CreateView):
    model      = SurveyResult
    form_class = cm_forms.SurveyResultForm

    def get_context_data(self, **kwargs):
        # xxx will be available in the template as the related objects
        context                = super(SurveyResultCreate, self).get_context_data(**kwargs)
        context['data_result'] = "''"
        context['student']     = Student.objects.filter(pk=self.kwargs['student_id'])
        groupsurvey            = GroupSurvey.objects.get(pk=self.kwargs['survey_id'])
        context['survey']      = groupsurvey
        try:
            survey = groupsurvey.survey
            if groupsurvey.is_expired():
                # survey is expired
                context['grading_template'] = ""
                context['info']             = ""
                context['input_fields']     = ""
            else:
                try:
                    grading_templates = SurveyGradingTemplate.objects.get(survey=survey)
                except:
                    grading_templates = []
                context['grading_template'] = grading_templates
                input_groups                = SurveyInputGroup.objects.filter(survey=survey)
                i_gr = []
                for ig in input_groups:
                    i_gr.append({
                        'group':  ig,
                        'inputs': SurveyInputField.objects.filter(input_group=ig)
                    })
                context['input_groups'] = i_gr
        except Exception as e:
            raise Exception("Ekki næst samband við prófagrunn")
        return context

    def post(self, *args, **kwargs):
        self.object          = None
        form                 = self.get_form()
        # make data mutable
        form.data            = self.request.POST.copy()
        form.data['student'] = Student.objects.get(pk=self.kwargs['student_id']).pk
        form.data['survey']  = GroupSurvey.objects.get(pk=self.kwargs['survey_id']).pk
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        survey_results             = form.save(commit=False)
        survey_results.reported_by = Teacher.objects.get(user_id=self.request.user.pk)
        survey_results.student     = Student.objects.get(pk=self.kwargs['student_id'])
        survey_results.survey      = GroupSurvey.objects.get(pk=self.kwargs['survey_id'])
        survey_results.created_at  = timezone.now()
        # extract data
        survey_results_data = {'click_values': [], 'input_values': {}}
        for k in self.request.POST:
            if k != 'csrfmiddlewaretoken':
                if k == 'data_results[]':
                    survey_results_data['click_values'] = json.dumps(
                        self.request.POST.getlist('data_results[]')
                    )
                else:
                    survey_results_data['input_values'][k] = self.request.POST[k]
        survey_results.results = json.dumps(survey_results_data)
        return super(SurveyResultCreate, self).form_valid(form)

    def get_success_url(self):
        try:
            survey = GroupSurvey.objects.get(pk=self.kwargs['survey_id'])
            return reverse_lazy(
                'schools:survey_detail',
                kwargs={
                    'pk'           : self.kwargs['survey_id'],
                    'school_id'    : self.kwargs['school_id'],
                    'student_group': survey.studentgroup.id
                }
            )
        except:
            return reverse_lazy('schools:school_listing')


class SurveyResultUpdate(common_mixins.SchoolEmployeeMixin, UpdateView):
    model      = SurveyResult
    form_class = cm_forms.SurveyResultForm

    def form_valid(self, form):
        survey_results            = form.save(commit=False)
        survey_results.created_at = timezone.now()
        # extract data
        survey_results_data       = {'click_values': [], 'input_values': {}}
        for k in self.request.POST:
            if k != 'csrfmiddlewaretoken':
                if k == 'data_results[]':
                    survey_results_data['click_values'] = json.dumps(
                        self.request.POST.getlist('data_results[]')
                    )
                else:
                    survey_results_data['input_values'][k] = self.request.POST[k]
        survey_results.results = json.dumps(survey_results_data)
        return super(SurveyResultUpdate, self).form_valid(form)

    def get_context_data(self, **kwargs):
        # xxx will be available in the template as the related objects
        context                     = super(SurveyResultUpdate, self).get_context_data(**kwargs)
        context['student']          = Student.objects.filter(pk=self.kwargs['student_id'])
        groupsurvey                 = GroupSurvey.objects.get(pk=self.kwargs['survey_id'])
        context['survey']           = GroupSurvey.objects.filter(pk=self.kwargs['survey_id'])
        context['data_result']      = json.loads(
            SurveyResult.objects.get(pk=self.kwargs['pk']).results
        ) or "''"
        survey = groupsurvey.survey
        try:
            grading_templates = SurveyGradingTemplate.objects.get(survey=survey)
        except:
            grading_templates = []
        context['grading_template'] = grading_templates
        input_groups                = SurveyInputGroup.objects.filter(survey=survey)
        i_gr = []
        for ig in input_groups:
            i_gr.append({
                'group':  ig,
                'inputs': SurveyInputField.objects.filter(input_group=ig)
            })
        context['input_groups'] = i_gr

        return context

    def get_success_url(self):
        try:
            survey = GroupSurvey.objects.get(pk=self.kwargs['survey_id'])
            return reverse_lazy(
                'schools:survey_detail',
                kwargs={
                    'pk'           : self.kwargs['survey_id'],
                    'school_id'    : self.kwargs['school_id'],
                    'student_group': survey.studentgroup.id
                }
            )
        except:
            return reverse_lazy('schools:school_listing')


class SurveyResultDelete(common_mixins.SchoolEmployeeMixin, DeleteView):
    model         = SurveyResult
    template_name = "schools/confirm_delete.html"

    def get_success_url(self):
        try:
            school_id = self.kwargs['school_id']
            return reverse_lazy(
                'schools:school_detail',
                kwargs={'pk': school_id}
            )
        except:
            return reverse_lazy('schools:school_listing')


class SurveyLoginListing(common_mixins.SchoolEmployeeMixin, ListView):
    model = SurveyLogin

    def get_context_data(self, **kwargs):
        # xxx will be available in the template as the related objects
        context                      = super(SurveyLoginListing, self).get_context_data(**kwargs)
        school                       = School.objects.get(pk=self.kwargs['school_id'])
        context['school_id']         = school.id
        survey_login_list = SurveyLogin.objects.filter(
            student__in = Student.objects.filter(school=school)
        ).values('survey_id').distinct()
        print(survey_login_list)
        context['survey_list'] = Survey.objects.filter(identifier__in =survey_login_list)
        return context


class SurveyLoginAdminListing(common_mixins.SuperUserMixin, ListView):
    model = SurveyLogin
    template_name = "common/surveylogin_admin_list.html"
    # Success url?

    def get_context_data(self, **kwargs):
        # xxx will be available in the template as the related objects
        context = super(SurveyLoginAdminListing, self).get_context_data(**kwargs)

        context['survey_login_list'] = SurveyLogin.objects.all(
        ).values('survey_id').distinct()
        return context


class SurveyLoginDetail(common_mixins.SchoolManagerMixin, DetailView):
    model = SurveyLogin

    def get_object(self, **kwargs):
        return SurveyLogin.objects.filter(survey_id=self.kwargs['survey_id']).first()

    def get_template_names(self, **kwargs):
        if 'print' in self.kwargs:
            if self.kwargs['print'] == 'listi':
                return ['surveylogin_detail_print_list.html']
            elif self.kwargs['print'] == 'einstaklingsblod':
                return ['surveylogin_detail_print_singles.html']
        return ['surveylogin_detail.html']

    def get_context_data(self, **kwargs):
        # xxx will be available in the template as the related objects
        context              = super(SurveyLoginDetail, self).get_context_data(**kwargs)
        context['survey_id'] = self.kwargs['survey_id']
        identifier = self.kwargs['survey_id']
        survey_name = Survey.objects.filter(identifier = identifier[:len(identifier)-11]).values('title')
        context['survey_name'] = survey_name[0]
        if 'school_id' in self.kwargs:
            school = School.objects.get(pk=self.kwargs['school_id'])

            context['survey_login_students'] = SurveyLogin.objects.filter(
                student__in = Student.objects.filter(school=school),
                survey_id   = self.kwargs['survey_id']
            )
        else:
            context['survey_login_students'] = SurveyLogin.objects.filter(
                survey_id=self.kwargs['survey_id']
            )
        if 'íslenska' in self.kwargs['survey_id']:
            context['exam'] = '1'
        elif 'enska' in self.kwargs['survey_id']:
            context['exam'] = '2'
        elif 'stærðfræði' in self.kwargs['survey_id']:
            context['exam'] = '3'
        return context


class SurveyLoginCreate(common_mixins.SuperUserMixin, CreateView):
    model         = SurveyLogin
    form_class    = cm_forms.SurveyLoginForm
    template_name = "common/password_form_import.html"

    def post(self, *args, **kwargs):
        if(self.request.FILES):
            u_file    = self.request.FILES['file'].name
            extension = u_file.split(".")[-1]
            ssn       = self.request.POST.get('student_ssn')
            survey_id = self.request.POST.get('survey_id')
            password  = self.request.POST.get('password')
            title     = self.request.POST.get('title')

            if title == 'yes':
                first = 1
            else:
                first = 0

            data = []
            try:
                if extension == 'csv':
                    for row in self.request.FILES['file'].readlines()[first:]:
                        row               = row.decode('utf-8')
                        student_ssn       = row.split(',')[int(ssn)]
                        student_survey_id = row.split(',')[int(survey_id)]
                        student_password  = row.split(',')[int(password)]
                        data.append({
                            'survey_id': student_survey_id.strip(),
                            'ssn'      : student_ssn.strip(),
                            'password' : student_password.strip()})
                elif extension == 'xlsx':
                    input_excel = self.request.FILES['file']
                    book        = xlrd.open_workbook(file_contents=input_excel.read())
                    for sheetsnumber in range(book.nsheets):
                        sheet = book.sheet_by_index(sheetsnumber)
                        for row in range(first, sheet.nrows):
                            data.append({
                                'survey_id': str(sheet.cell_value(row, int(survey_id))),
                                'ssn'      : str(sheet.cell_value(row, int(ssn))),
                                'password' : str(sheet.cell_value(row, int(password))),
                            })
                return render(self.request, 'common/password_verify_import.html', {'data': data})
            except Exception as e:
                return render(
                    self.request,
                    'common/password_form_import.html',
                    {'error': 'Dálkur ekki til, reyndu aftur'}
                )

        else:
            student_data = json.loads(self.request.POST['students'])
            # Iterate through the data
            # Add students if they don't exist then create a survey_login object
            for data in student_data:
                student = Student.objects.get(ssn=data['ssn'])  # student already exists

                # check if survey_login for student exists, create if not, otherwise update
                survey_login = SurveyLogin.objects.filter(
                    student   = student,
                    survey_id = data['survey_id']
                )
                if survey_login:
                    survey_login.update(survey_code=data['password'])
                else:
                    survey_login = SurveyLogin.objects.create(
                        student     = student,
                        survey_id   = data['survey_id'],
                        survey_code = data['password']
                    )
        return redirect(self.get_success_url())

    def get_success_url(self):
        return reverse_lazy('schools:survey_login_admin_listing')


class SurveyLoginDelete(common_mixins.SuperUserMixin, DeleteView):
    model         = SurveyLogin
    template_name = "schools/confirm_delete.html"

    def get_success_url(self):
        return reverse_lazy('schools:survey_login_admin_listing')

    def get_object(self):
        return SurveyLogin.objects.filter(survey_id=self.kwargs['survey_id'])


class AdminListing(common_mixins.SuperUserMixin, ListView):
    model         = User
    template_name = "common/admin_list.html"

    def get_success_url(self):
        return reverse_lazy('schools:admin_listing')

    def get_context_data(self, **kwargs):
        # xxx will be available in the template as the related objects
        context              = super(AdminListing, self).get_context_data(**kwargs)
        context['user_list'] = User.objects.filter(is_superuser=True)
        return context


class AdminCreate(common_mixins.SuperUserMixin, CreateView):
    model         = User
    form_class    = cm_forms.SuperUserForm
    template_name = "common/admin_form.html"

    def post(self, *args, **kwargs):
        username     = self.request.POST.get('username')
        is_superuser = self.request.POST.get('is_superuser', False)
        if User.objects.filter(username=username).exists():
            if is_superuser:
                User.objects.filter(username=username).update(is_superuser=True)
        else:
            User.objects.create_user(
                username=username,
                is_superuser=is_superuser
            )
        return redirect(self.get_success_url())

    def get_success_url(self):
        return reverse_lazy('schools:admin_listing')


class AdminUpdate(common_mixins.SuperUserMixin, UpdateView):
    model         = User
    form_class    = cm_forms.SuperUserForm
    template_name = "common/admin_form.html"

    def get_success_url(self):
        return reverse_lazy('schools:admin_listing')


def group_admin_listing_excel(request, survey_title):
    surveys = GroupSurvey.objects.filter(survey__title=survey_title)
    response                        = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=samræmdupróf.xlsx'
    wb                              = openpyxl.Workbook()

    ws       = wb.get_active_sheet()
    ws.title = 'samræmdupróf'
    ws['A1'] = 'FIRST'
    ws['B1'] = 'LAST'
    ws['C1'] = 'RESULTS EMAIL'
    ws['D1'] = 'EXTERNAL ID'
    ws['E1'] = 'CODE EMAIL'
    ws['F1'] = 'TEST NAME'
    ws['G1'] = 'GROUP PATH'
    ws['H1'] = 'EXTRA TIME'
    ws['J1'] = 'BEKKUR (TAKA ÚT)'

    index = 2
    for survey in surveys:
        if survey.studentgroup:
            for student in survey.studentgroup.students.all():
                studentname = student.name
                studentpos = [pos for pos, char in enumerate(studentname) if char == ' '][-1]
                ws.cell('A' + str(index)).value = studentname[0:studentpos]
                ws.cell('B' + str(index)).value = studentname[studentpos:]
                ws.cell('D' + str(index)).value = student.ssn
                ws.cell('F' + str(index)).value = survey.survey.identifier
                ws.cell('H' + str(index)).value = 'N'
                #print(student.id)
                supports = SupportResource.objects.filter(student=student.id)
                for support in supports:
                    if 'fyrri' in survey_title and '1' in support.longer_time or '2' in support.longer_time:
                        ws.cell('H' + str(index)).value = 'Y'
                    elif'seinni' in survey_title and '3' in support.longer_time or '2' in support.longer_time:
                        ws.cell('H' + str(index)).value = 'Y'

                ws.cell('J' + str(index)).value = str(StudentGroup.objects.filter(students=student.id)[:1].get())
                index += 1

    wb.save(response)

    return response


def group_admin_attendance_excel(request, survey_title):

    surveys  = GroupSurvey.objects.filter(survey__title=survey_title)
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=samræmdupróf.xlsx'

    wb       = openpyxl.Workbook()
    ws       = wb.get_active_sheet()
    ws.title = 'samræmdupróf'

    ws['A1'] = 'Skóli'
    ws['B1'] = 'Kennitala sḱóla'
    ws['C1'] = 'Nemandi'
    ws['D1'] = 'Kennitala'
    ws['E1'] = 'Bekkur'
    ws['F1'] = 'Mættur'
    ws['G1'] = 'Undanþága'
    ws['H1'] = 'Veikur'
    ws['I1'] = 'Fjarverandi'
    ws['J1'] = 'Stuðningur í íslensku'
    ws['K1'] = 'Stuðningur í Stærðfræði'

    index = 2
    for survey in surveys:
        if survey.studentgroup:
            for student in survey.studentgroup.students.all():
                ws.cell('A' + str(index)).value = survey.studentgroup.school.name
                ws.cell('B' + str(index)).value = survey.studentgroup.school.ssn
                ws.cell('C' + str(index)).value = student.name
                ws.cell('D' + str(index)).value = student.ssn
                ws.cell('E' + str(index)).value = survey.studentgroup.name

                sr              = SurveyResult.objects.filter(student=student, survey=survey)
                student_results = ""
                if sr:
                    r = literal_eval(sr.first().results)  # get student results
                    try:
                        student_results = int(r['click_values'][2])
                    except Exception as e:
                        print(e)
                else:
                    student_results = ''

                if student_results != '':
                    ws.cell(row=index, column=student_results + 6).value = "1"

                support = sae_models.SupportResource.objects.filter(student=student)

                if support:
                    support_available = []
                    support_available += literal_eval(support.first().reading_assistance)
                    support_available += literal_eval(support.first().interpretation)
                    support_available += literal_eval(support.first().longer_time)
                    if 1 in support_available:
                        ws.cell(row=index, column=10).value = "1"
                    if 3 in support_available:
                        ws.cell(row=index, column=11).value = "1"

                index += 1

    wb.save(response)

    return response


def survey_detail_excel(request, school_id, student_group, pk):
        school = School.objects.get(pk=school_id)
        studentgroup = StudentGroup.objects.get(pk=student_group)
        survey = GroupSurvey.objects.filter(pk=pk).first()

        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename=Niðurstöður - {}.xlsx'.format(survey.survey.title)
        wb = openpyxl.Workbook()
        ws = wb.get_active_sheet()

        identifier = survey.survey.identifier

        if identifier.startswith('01b_LTL_'):
            ws.title = 'Lesskimun fyrir fyrsta bekk'

            ws['A1'] = 'Kennitala'
            ws['B1'] = 'Nafn'
            ws['C1'] = 'Hljóð'
            ws['D1'] = 'Mál'
            ws['E1'] = 'Stafir'

            index = 2
            if studentgroup:
                for student in studentgroup.students.all():
                    ws.cell('A' + str(index)).value = student.ssn
                    ws.cell('B' + str(index)).value = student.name
                    sr = SurveyResult.objects.filter(student=student, survey=survey)
                    if sr:
                        r = literal_eval(sr.first().results)  # get student results
                        survey_student_result = common_util.calc_survey_results(
                            identifier,
                            [],
                            r['input_values'],
                            student
                        )
                        ws.cell('C' + str(index)).value = survey_student_result[0]
                        ws.cell('D' + str(index)).value = survey_student_result[1]
                        ws.cell('E' + str(index)).value = survey_student_result[2]
                    else:
                        ws.cell('C' + str(index)).value = 'Vantar gögn'
                        ws.cell('D' + str(index)).value = 'Vantar gögn'
                        ws.cell('E' + str(index)).value = 'Vantar gögn'
                    index += 1
        elif identifier.endswith('_LF_jan17'):
            ws.title = 'Niðurstöður'
            ws['A1'] = 'Kennitala'
            ws['B1'] = 'Nafn'
            ws['C1'] = 'September'
            ws['D1'] = 'Janúar'
            ws['E1'] = 'Mismunur'

            ref_values = {
                '1':  (20, 55, 75),
                '2':  (40, 85, 100),
                '3':  (55, 100, 120),
                '4':  (80, 120, 145),
                '5':  (90, 140, 160),
                '6':  (105, 155, 175),
                '7':  (120, 165, 190),
                '8':  (130, 180, 210),
                '9':  (140, 180, 210),
                '10': (145, 180, 210),
            }

            index = 2
            survey_type = SurveyType.objects.filter(survey=survey.survey.id).values('id')
            dic = survey_type[0]
            survey_type = dic['id']
            jan_transformation = SurveyTransformation.objects.filter(survey=survey.survey)

            datapoints = []
            datapoints.append(('Nafn', 'September', 'Janúar', '90% viðmið', '50% viðmið', '25% viðmið'))

            if studentgroup:
                sept_identifier = "{}b_LF_sept".format(studentgroup.student_year)
                sept_survey = Survey.objects.filter(identifier = sept_identifier).first()
                sept_transformation = SurveyTransformation.objects.filter(survey=sept_survey)
                sept_gs = GroupSurvey.objects.filter(survey = sept_survey, studentgroup = survey.studentgroup).first()

                for student in studentgroup.students.all():
                    value_jan = 'Vantar gögn'
                    value_sept = 'Vantar gögn'
                    ws.cell('A' + str(index)).value = student.ssn
                    ws.cell('B' + str(index)).value = student.name
                    sy = studentgroup.student_year
                    sr = SurveyResult.objects.filter(student=student, survey=survey)
                    if sr:
                        r = literal_eval(sr.first().results)  # get student results
                        try:
                            click_values = literal_eval(r['click_values'])
                        except:
                            click_values = []
                        survey_student_result = common_util.calc_survey_results(
                            survey_identifier = identifier,
                            click_values = click_values,
                            input_values = r['input_values'],
                            student = student,
                            survey_type = survey_type,
                            transformation = jan_transformation,
                        )
                        value_jan = survey_student_result[0]

                    sr = SurveyResult.objects.filter(student=student, survey=sept_gs)
                    if sr:
                        r = literal_eval(sr.first().results)  # get student results
                        try:
                            click_values = literal_eval(r['click_values'])
                        except:
                            click_values = []
                        survey_student_result = common_util.calc_survey_results(
                            survey_identifier = sept_identifier,
                            click_values = click_values,
                            input_values = r['input_values'],
                            student = student,
                            survey_type = survey_type,
                            transformation = sept_transformation,
                        )
                        value_sept = survey_student_result[0]

                    ws.cell('C' + str(index)).value = value_sept
                    ws.cell('D' + str(index)).value = value_jan
                    if isinstance(value_sept, int) and isinstance(value_jan, int):
                        cur_cell = ws.cell('E' + str(index))
                        diff = value_jan - value_sept

                        # Student year
                        if int(sy) <= 3:
                            if diff <= 7:
                                cur_cell.fill = PatternFill(start_color='ff0000', end_color='ff0000', fill_type="solid")

                            elif diff <= 20:
                                cur_cell.fill = PatternFill(start_color= 'ffff00', end_color= 'ffff00', fill_type="solid")
                            else:
                                cur_cell.fill = PatternFill(start_color= '00ff00', end_color= '00ff00', fill_type="solid")
                        else:
                            if diff < 0:
                                cur_cell.fill = PatternFill(start_color='ff0000', end_color='ff0000', fill_type="solid")

                            elif diff <= 10:
                                cur_cell.fill = PatternFill(start_color= 'ffff00', end_color= 'ffff00', fill_type="solid")
                            else:
                                cur_cell.fill = PatternFill(start_color= '00ff00', end_color= '00ff00', fill_type="solid")

                        cur_cell.value = diff

                    if not isinstance(value_sept, int):
                        value_sept = 0
                    if not isinstance(value_jan, int):
                        value_jan = 0

                    datapoints.append((student.name.split()[0], value_sept, value_jan, ref_values[sy][0], ref_values[sy][1], ref_values[sy][2]))

                    index += 1

            # Fix column widths
            dims = {}
            for row in ws.rows:
                for cell in row:
                    if cell.value:
                        dims[cell.column] = max((dims.get(cell.column, 0), len(str(cell.value))))
            for col, value in dims.items():
                ws.column_dimensions[col].width = int(value) + 2

            # Add legend
            index += 2
            ws.cell('A' + str(index)).fill = PatternFill(start_color='ff0000', end_color='ff0000', fill_type='solid')
            ws.cell('B' + str(index)).value = 'Lítil framvinda miðað við aldur'
            ws.merge_cells('B' + str(index) + ':E' + str(index))
            index += 1
            ws.cell('A' + str(index)).fill = PatternFill(start_color='ffff00', end_color='ffff00', fill_type='solid')
            ws.cell('B' + str(index)).value = 'Fremur lítil framvinda'
            ws.merge_cells('B' + str(index) + ':E' + str(index))
            index += 1
            ws.cell('A' + str(index)).fill = PatternFill(start_color='00ff00', end_color='00ff00', fill_type='solid')
            ws.cell('B' + str(index)).value = 'Góð framvinda'
            ws.merge_cells('B' + str(index) + ':E' + str(index))

            # Add bar chart
            ws_bar = wb.create_sheet(title="Súlurit")
            for datapoint in datapoints:
                ws_bar.append(datapoint)
            chart = BarChart()
            chart.type = "col"
            chart.style = 10
            chart.title = "Niðurstöður úr Lesfimi, sept 2016 - jan 2017"
            chart.y_axis.title = "Orð á mínútu"
            chart.x_axis.title = "Nemandi"
            data = Reference(ws_bar, min_col=2, min_row=1, max_row=len(datapoints), max_col=3)
            cats = Reference(ws_bar, min_col=1, min_row=2, max_row=len(datapoints))
            chart.add_data(data, titles_from_data=True)
            chart.set_categories(cats)
            chart.shape = 4
            chart.width = 40
            chart.height = 20

            # Add reference lines
            lchart = LineChart()
            ldata = Reference(ws_bar, min_col=4, max_col=6, min_row=1, max_row=len(datapoints) + 1)
            lchart.width = 40
            lchart.height = 20

            lchart.layout = Layout(
                ManualLayout(
                    xMode="edge",
                    yMode="edge",
                )
            )
            lchart.add_data(ldata, titles_from_data=True)
            chart += lchart

            for idx in range(1, len(datapoints) + 1):
                ws_bar.row_dimensions[idx].hidden = True

            ws_bar.add_chart(chart, "A" + str(len(datapoints) + 1))

        wb.save(response)

        return response


def lesfimi_excel_for_principals(request, pk):
    ref_values = {
        1:  (20, 55, 75),
        2:  (40, 85, 100),
        3:  (55, 100, 120),
        4:  (80, 120, 145),
        5:  (90, 140, 160),
        6:  (105, 155, 175),
        7:  (120, 165, 190),
        8:  (130, 180, 210),
        9:  (140, 180, 210),
        10: (145, 180, 210),
    }

    # Get the school object
    school = School.objects.get(pk = pk)

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=Lesfimi {}.xlsx'.format(school.name)

    wb = openpyxl.Workbook()
    ws = wb.get_active_sheet()
    wb.remove_sheet(ws)

    tests = (
        ('b{}_LF_jan17', 'Janúar 2017'),
        ('{}b_LF_sept', 'September 2016'),
    )
    for test in tests:
        identifier = test[0]
        title = test[1]
        ws = wb.create_sheet(title = title)
        ws['A1'] = 'Árgangur'
        ws['B1'] = 'Fjöldi nemenda'
        ws['C1'] = 'Fjöldi sem þreytti próf'
        ws['D1'] = 'Hlutfall sem þreytti próf'
        ws['E1'] = 'Hlutfall sem nær 90% viðmiðum'
        ws['F1'] = 'Hlutfall sem nær 50% viðmiðum'
        ws['G1'] = 'Hlutfall sem nær 25% viðmiðum'
        index = 2
        errors = []
        for year in range(1, 11):
            ws['A' + str(index)] = year
            survey = Survey.objects.filter(identifier = identifier.format(year)).first()
            survey_type = SurveyType.objects.filter(survey=survey.id).values('id')
            dic = survey_type[0]
            survey_type = dic['id']
            transformation = SurveyTransformation.objects.filter(survey=survey)
            studentgroups = StudentGroup.objects.filter(school = school, student_year = year).all()
            this_year_result = {
                'students': 0,
                'students_who_took_test': 0,
                'students_over_25pct': 0,
                'students_over_50pct': 0,
                'students_over_90pct': 0,
            }
            for studentgroup in studentgroups:
                this_year_result['students'] += studentgroup.students.all().count()
                groupsurveys = GroupSurvey.objects.filter(studentgroup = studentgroup, survey = survey)
                if groupsurveys.all().count() > 1:
                    errors.append('sama próf skráð {} sinnum fyrir {}'.format(groupsurveys.all().count(), studentgroup.name))
                for groupsurvey in groupsurveys.all():
                    for student in studentgroup.students.all():
                        surveyresults = SurveyResult.objects.filter(survey = groupsurvey, student = student)
                        if surveyresults.all().count() > 1:
                            errors.append('{} niðurstöður í sama prófi skráðar fyrir nemanda {} í bekk {}'.format(
                                surveyresults.all().count(),
                                student.ssn,
                                studentgroup.name,
                            ))
                        for surveyresult in surveyresults.all():
                            r = literal_eval(surveyresult.results)  # get student results
                            try:
                                survey_student_result = common_util.calc_survey_results(
                                    survey_identifier = identifier,
                                    click_values = literal_eval(r['click_values']),
                                    input_values = r['input_values'],
                                    student = student,
                                    survey_type = survey_type,
                                    transformation = transformation,
                                )
                                # import pdb; pdb.set_trace()
                                if not survey_student_result[0] == '':
                                    this_year_result['students_who_took_test'] += 1
                                    if int(survey_student_result[0]) >= ref_values[year][2]:
                                        this_year_result['students_over_25pct'] += 1
                                    if int(survey_student_result[0]) >= ref_values[year][1]:
                                        this_year_result['students_over_50pct'] += 1
                                    if int(survey_student_result[0]) >= ref_values[year][0]:
                                        this_year_result['students_over_90pct'] += 1
                            except:
                                pass

            ws['B' + str(index)] = this_year_result['students']
            ws['C' + str(index)] = this_year_result['students_who_took_test']
            if this_year_result['students'] > 0 and this_year_result['students_who_took_test'] > 0:
                ws['D' + str(index)] = (this_year_result['students_who_took_test'] / this_year_result['students']) * 100
                pct_over_90pct = (this_year_result['students_over_90pct'] / this_year_result['students_who_took_test']) * 100
                ws['E' + str(index)] = pct_over_90pct

                pct_over_50pct = (this_year_result['students_over_50pct'] / this_year_result['students_who_took_test']) * 100
                ws['F' + str(index)] = pct_over_50pct

                pct_over_25pct = (this_year_result['students_over_25pct'] / this_year_result['students_who_took_test']) * 100
                ws['G' + str(index)] = pct_over_25pct

            else:
                ws['D' + str(index)] = 0
                ws['E' + str(index)] = 0
                ws['F' + str(index)] = 0
                ws['G' + str(index)] = 0

            index += 1
        dims = {}
        for row in ws.rows:
            for cell in row:
                if cell.value:
                    dims[cell.column] = max((dims.get(cell.column, 0), len(str(cell.value))))
        for col, value in dims.items():
            ws.column_dimensions[col].width = int(value) + 2

        chart = AreaChart()
        chart.title = "Lesfimi í {} - {}".format(title, school.name)
        chart.style = 10
        chart.width = 40
        chart.height = 20

        chart.layout = Layout(
            ManualLayout(
                xMode="edge",
                yMode="edge",
            )
        )

        chart.x_axis.title = 'Árgangur'
        chart.y_axis.title = 'Prósent'

        chart.y_axis.scaling.min = 0
        chart.y_axis.scaling.max = 100

        cats = Reference(ws, min_col=1, min_row=2, max_row=index - 1)
        data = Reference(ws, min_col=5, min_row=1, max_col=7, max_row=index)
        chart.add_data(data, titles_from_data=True)
        chart.set_categories(cats)

        bchart = BarChart()
        bchart.title = "Hlutfall nemenda sem þreyttu próf"
        bchart.style = 10
        bchart.width = 20
        bchart.height = 10

        bchart.x_axis.title = 'Árgangur'
        bchart.y_axis.title = 'Prósent'

        bchart.y_axis.scaling.min = 0
        bchart.y_axis.scaling.max = 100

        bdata = Reference(ws, min_col=4, max_col=4, min_row=2, max_row=index)
        bchart.add_data(bdata)
        bchart.legend = None
        bchart.set_categories(cats)
        ws.add_chart(bchart, "I1")

        if errors:
            index += 1
            for error in errors:
                ws['A' + str(index)] = "ATH: " + error
                ws['A' + str(index)].fill = PatternFill(start_color='ff0000', end_color='ff0000', fill_type='solid')
                ws.merge_cells('A' + str(index) + ':F' + str(index))
                index += 1
        if index > 20:
            ws.add_chart(chart, "A" + str(index + 2))
        else:
            ws.add_chart(chart, "A22")

    # wb.save(filename='/tmp/test.xlsx')
    wb.save(response)

    return response


def lesfimi_excel_entire_country_stats():
    ref_values = {
        1:  (20, 55, 75),
        2:  (40, 85, 100),
        3:  (55, 100, 120),
        4:  (80, 120, 145),
        5:  (90, 140, 160),
        6:  (105, 155, 175),
        7:  (120, 165, 190),
        8:  (130, 180, 210),
        9:  (140, 180, 210),
        10: (145, 180, 210),
    }

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=Lesfimi - Allt Landið.xlsx'

    wb = openpyxl.Workbook()
    ws = wb.get_active_sheet()
    wb.remove_sheet(ws)

    tests = (
        ('b{}_LF_jan17', 'Janúar 2017'),
        ('{}b_LF_sept', 'September 2016'),
    )
    for test in tests:
        identifier = test[0]
        title = test[1]
        ws = wb.create_sheet(title = title)
        ws['A1'] = 'Árgangur'
        ws['B1'] = 'Fjöldi nemenda'
        ws['C1'] = 'Fjöldi sem þreytti próf'
        ws['D1'] = 'Hlutfall sem þreytti próf'
        ws['E1'] = 'Hlutfall sem nær 90% viðmiðum'
        ws['F1'] = 'Hlutfall sem nær 50% viðmiðum'
        ws['G1'] = 'Hlutfall sem nær 25% viðmiðum'
        index = 2
        errors = []
        for year in range(1, 11):
            ws['A' + str(index)] = year
            survey = Survey.objects.filter(identifier = identifier.format(year)).first()
            survey_type = SurveyType.objects.filter(survey=survey.id).values('id')
            dic = survey_type[0]
            survey_type = dic['id']
            transformation = SurveyTransformation.objects.filter(survey=survey)
            studentgroups = StudentGroup.objects.filter(student_year = year).all()
            this_year_result = {
                'students': 0,
                'students_who_took_test': 0,
                'students_over_25pct': 0,
                'students_over_50pct': 0,
                'students_over_90pct': 0,
            }
            for studentgroup in studentgroups:
                this_year_result['students'] += studentgroup.students.all().count()
                groupsurveys = GroupSurvey.objects.filter(studentgroup = studentgroup, survey = survey)
                if groupsurveys.all().count() > 1:
                    errors.append('sama próf skráð {} sinnum fyrir {} í {}'.format(groupsurveys.all().count(), studentgroup.name, studentgroup.school.name))
                for groupsurvey in groupsurveys.all():
                    for student in studentgroup.students.all():
                        surveyresults = SurveyResult.objects.filter(survey = groupsurvey, student = student)
                        if surveyresults.all().count() > 1:
                            errors.append('{} niðurstöður í sama prófi skráðar fyrir nemanda {} í bekk {} í {}'.format(
                                surveyresults.all().count(),
                                student.ssn,
                                studentgroup.name,
                                studentgroup.school.name,
                            ))
                        for surveyresult in surveyresults.all():
                            r = literal_eval(surveyresult.results)  # get student results
                            try:
                                survey_student_result = common_util.calc_survey_results(
                                    survey_identifier = identifier,
                                    click_values = literal_eval(r['click_values']),
                                    input_values = r['input_values'],
                                    student = student,
                                    survey_type = survey_type,
                                    transformation = transformation,
                                )
                                # import pdb; pdb.set_trace()
                                if not survey_student_result[0] == '':
                                    this_year_result['students_who_took_test'] += 1
                                    if int(survey_student_result[0]) >= ref_values[year][2]:
                                        this_year_result['students_over_25pct'] += 1
                                    if int(survey_student_result[0]) >= ref_values[year][1]:
                                        this_year_result['students_over_50pct'] += 1
                                    if int(survey_student_result[0]) >= ref_values[year][0]:
                                        this_year_result['students_over_90pct'] += 1
                            except:
                                pass

            ws['B' + str(index)] = this_year_result['students']
            ws['C' + str(index)] = this_year_result['students_who_took_test']
            if this_year_result['students'] > 0 and this_year_result['students_who_took_test'] > 0:
                ws['D' + str(index)] = (this_year_result['students_who_took_test'] / this_year_result['students']) * 100
                pct_over_90pct = (this_year_result['students_over_90pct'] / this_year_result['students_who_took_test']) * 100
                ws['E' + str(index)] = pct_over_90pct

                pct_over_50pct = (this_year_result['students_over_50pct'] / this_year_result['students_who_took_test']) * 100
                ws['F' + str(index)] = pct_over_50pct

                pct_over_25pct = (this_year_result['students_over_25pct'] / this_year_result['students_who_took_test']) * 100
                ws['G' + str(index)] = pct_over_25pct

            else:
                ws['D' + str(index)] = 0
                ws['E' + str(index)] = 0
                ws['F' + str(index)] = 0
                ws['G' + str(index)] = 0

            index += 1
        dims = {}
        for row in ws.rows:
            for cell in row:
                if cell.value:
                    dims[cell.column] = max((dims.get(cell.column, 0), len(str(cell.value))))
        for col, value in dims.items():
            ws.column_dimensions[col].width = int(value) + 2

        chart = AreaChart()
        chart.title = "Lesfimi í {} - Allt landið".format(title)
        chart.style = 10
        chart.width = 40
        chart.height = 20

        chart.layout = Layout(
            ManualLayout(
                xMode="edge",
                yMode="edge",
            )
        )

        chart.x_axis.title = 'Árgangur'
        chart.y_axis.title = 'Prósent'

        chart.y_axis.scaling.min = 0
        chart.y_axis.scaling.max = 100

        cats = Reference(ws, min_col=1, min_row=2, max_row=index - 1)
        data = Reference(ws, min_col=5, min_row=1, max_col=7, max_row=index)
        chart.add_data(data, titles_from_data=True)
        chart.set_categories(cats)

        bchart = BarChart()
        bchart.title = "Hlutfall nemenda sem þreyttu próf"
        bchart.style = 10
        bchart.width = 20
        bchart.height = 10

        bchart.x_axis.title = 'Árgangur'
        bchart.y_axis.title = 'Prósent'

        bchart.y_axis.scaling.min = 0
        bchart.y_axis.scaling.max = 100

        bdata = Reference(ws, min_col=4, max_col=4, min_row=2, max_row=index)
        bchart.add_data(bdata)
        bchart.legend = None
        bchart.set_categories(cats)
        ws.add_chart(bchart, "I1")

        if index > 20:
            ws.add_chart(chart, "A" + str(index + 2))
        else:
            ws.add_chart(chart, "A22")

        if errors:
            ws = wb.create_sheet(title = 'Villur')
            index = 1
            for error in errors:
                ws['A' + str(index)] = "ATH: " + error
                ws['A' + str(index)].fill = PatternFill(start_color='ff0000', end_color='ff0000', fill_type='solid')
                ws.merge_cells('A' + str(index) + ':F' + str(index))
                index += 1

    wb.save(filename='/tmp/test.xlsx')
    # wb.save(response)

    return response


def _lesfimi_excel_result_duplicates():
    wb = openpyxl.Workbook()
    ws = wb.get_active_sheet()
    wb.remove_sheet(ws)

    tests = (
        ('b{}_LF_jan17', 'Janúar 2017'),
        ('{}b_LF_sept', 'September 2016'),
    )
    for test in tests:
        identifier = test[0]
        title = test[1]
        ws = wb.create_sheet(title = title)
        ws['A1'] = 'Kennitala'
        ws['B1'] = 'Groupsurvey id'
        ws['C1'] = 'Surveyresult id'
        ws['D1'] = 'Result'
        index = 2
        errors = []
        for year in range(1, 11):
            ws['A' + str(index)] = year
            survey = Survey.objects.filter(identifier = identifier.format(year)).first()
            survey_type = SurveyType.objects.filter(survey=survey.id).values('id')
            dic = survey_type[0]
            survey_type = dic['id']
            transformation = SurveyTransformation.objects.filter(survey=survey)
            studentgroups = StudentGroup.objects.filter(student_year = year).all()
            for studentgroup in studentgroups:
                groupsurveys = GroupSurvey.objects.filter(studentgroup = studentgroup, survey = survey)
                if groupsurveys.all().count() > 1:
                    errors.append('sama próf skráð {} sinnum fyrir {} í {}'.format(groupsurveys.all().count(), studentgroup.name, studentgroup.school.name))
                for groupsurvey in groupsurveys.all():
                    for student in studentgroup.students.all():
                        surveyresults = SurveyResult.objects.filter(survey = groupsurvey, student = student)
                        if surveyresults.all().count() > 1:
                            for surveyresult in surveyresults.all():
                                ws['A' + str(index)] = student.ssn
                                ws['B' + str(index)] = groupsurvey.id
                                ws['C' + str(index)] = surveyresult.id
                                ws['D' + str(index)] = surveyresult.results
                                index += 1
    
    wb.save(filename='/tmp/duplicates.xlsx')
