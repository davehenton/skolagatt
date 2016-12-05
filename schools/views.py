# -*- coding: utf-8 -*-
from django.http                  import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts             import render, get_object_or_404, redirect
from django.views.generic         import ListView, CreateView, DetailView, UpdateView, DeleteView
from django.core.urlresolvers     import reverse_lazy
from django.contrib.auth.mixins   import UserPassesTestMixin
from django.contrib.auth.models   import User
from django.conf                  import settings
from django.utils                 import timezone
from django.utils.decorators      import method_decorator
from django.views.decorators.csrf import csrf_exempt

from uuid     import uuid4
from datetime import datetime, date
from ast      import literal_eval

import requests
import json
import xlrd
import openpyxl
import csv

import common.mixins as common_mixins
import common.models as cm_models
import common.util   as common_util

import supportandexception.models as sae_models


def lesferill(request, school_id):
    return render(request, 'common/lesferill.html', {'school_id': school_id})


class NotificationCreate(UserPassesTestMixin, CreateView):
    model = cm_models.Notification

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(NotificationCreate, self).dispatch(request, *args, **kwargs)

    def test_func(self):
        return self.request.user.is_authenticated

    def post(self, *args, **kwargs):
        try:
            notification_type = self.request.POST.get('notification_type', None)
            notification_id   = self.request.POST.get('id', None)

            if notification_type and notification_id:
                cm_models.Notification.objects.create(
                    user              = self.request.user,
                    notification_type = notification_type,
                    notification_id   = notification_id)

            return JsonResponse({'result': 'success'})
        except Exception as e:
            return JsonResponse({'result': 'error'})


class SchoolListing(ListView):
    model = cm_models.School

    def get_context_data(self, **kwargs):
        context = super(SchoolListing, self).get_context_data(**kwargs)
        try:
            if self.request.user.is_superuser:
                context['school_list'] = common_util.slug_sort(
                    cm_models.School.objects.all(), 'name')
            else:
                manager_schools        = cm_models.School.objects.filter(
                    managers=cm_models.Manager.objects.filter(user=self.request.user))
                teacher_schools        = cm_models.School.objects.filter(
                    teachers=cm_models.Teacher.objects.filter(user=self.request.user))
                context['school_list'] = list(
                    set(common_util.slug_sort(manager_schools | teacher_schools, 'name')))
        except Exception as e:
            pass
        return context


class SchoolDetail(common_mixins.SchoolEmployeeMixin, DetailView):
    model = cm_models.School

    def get_context_data(self, **kwargs):
        context                      = super(SchoolDetail, self).get_context_data(**kwargs)
        context['studentgroup_list'] = common_util.slug_sort(
            self.object.studentgroup_set.all(), 'name')
        context['managers']          = common_util.slug_sort(
            self.object.managers.all(), 'name')
        context['teachers']          = common_util.slug_sort(
            self.object.teachers.all(), 'name')
        context['surveys']           = common_util.slug_sort(
            cm_models.Survey.objects.filter(
                studentgroup__in=self.object.studentgroup_set.all()), 'title')
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
    model       = cm_models.School
    form_class  = cm_models.SchoolForm
    success_url = reverse_lazy('schools:school_listing')


class SchoolCreateImport(common_mixins.SchoolManagerMixin, CreateView):
    model         = cm_models.School
    form_class    = cm_models.SchoolForm
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
                    cm_models.School.objects.create(**school)
                except:
                    pass  # student already exists

        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
            return reverse_lazy('schools:school_listing')


class SchoolUpdate(common_mixins.SuperUserMixin, UpdateView):
    model       = cm_models.School
    form_class  = cm_models.SchoolForm
    success_url = reverse_lazy('schools:school_listing')


class SchoolDelete(common_mixins.SuperUserMixin, DeleteView):
    model         = cm_models.School
    template_name = "schools/confirm_delete.html"
    success_url   = reverse_lazy('schools:school_listing')


class ManagerListing(common_mixins.SchoolEmployeeMixin, ListView):
    model = cm_models.Manager

    def get_context_data(self, **kwargs):
        context             = super(ManagerListing, self).get_context_data(**kwargs)
        school              = cm_models.School.objects.get(pk=self.kwargs['school_id'])
        context['school']   = school
        context['managers'] = cm_models.Manager.objects.filter(school=school)
        return context


class ManagerDetail(common_mixins.SchoolEmployeeMixin, DetailView):
    model = cm_models.Manager

    def get_context_data(self, **kwargs):
        context           = super(ManagerDetail, self).get_context_data(**kwargs)
        context['school'] = cm_models.School.objects.get(pk=self.kwargs['school_id'])
        return context


class ManagerOverview(UserPassesTestMixin, DetailView):
    model = cm_models.Manager

    def test_func(self):
        try:
            if self.request.user.id == cm_models.Manager.objects.get(pk=self.kwargs['pk']).user.id:
                return True
        except:
            return False
        return False

    def get_context_data(self, **kwargs):
        context           = super(ManagerOverview, self).get_context_data(**kwargs)
        context['school'] = cm_models.School.objects.filter(
            managers=cm_models.Manager.objects.filter(
                pk=self.kwargs['pk'])).first()
        return context


class ManagerCreate(common_mixins.SchoolManagerMixin, CreateView):
    model      = cm_models.Manager
    form_class = cm_models.ManagerForm

    def get_context_data(self, **kwargs):
        context           = super(ManagerCreate, self).get_context_data(**kwargs)
        context['school'] = cm_models.School.objects.get(pk=self.kwargs['school_id'])
        return context

    def post(self, *args, **kwargs):
        self.object = cm_models.Manager.objects.filter(
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
            cm_models.School.objects.get(pk=school_id).managers.add(self.object)
            return reverse_lazy(
                'schools:school_detail',
                kwargs={'pk': school_id})
        except:
            return reverse_lazy('schools:school_listing')

    def get_initial(self):
        school = get_object_or_404(cm_models.School, pk=self.kwargs.get('school_id'))
        return {
            'school': school,
        }


class ManagerCreateImport(common_mixins.SchoolManagerMixin, CreateView):
    model         = cm_models.School
    form_class    = cm_models.SchoolForm
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
                    cm_models.School.objects.get(
                        ssn=manager['school_ssn']
                    ).managers.add(**manager)
                except:
                    pass  # manager already exists

        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
            return reverse_lazy('schools:school_listing')


class ManagerUpdate(common_mixins.SchoolManagerMixin, UpdateView):
    model      = cm_models.Manager
    form_class = cm_models.ManagerForm

    def get_context_data(self, **kwargs):
        context           = super(ManagerUpdate, self).get_context_data(**kwargs)
        context['school'] = cm_models.School.objects.get(pk=self.kwargs['school_id'])
        return context

    def post(self, request, **kwargs):
        # get Manager to be updated
        self.object = cm_models.Manager.objects.get(pk=self.kwargs['pk'])
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
    model         = cm_models.Manager
    template_name = "schools/confirm_delete.html"

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        # delete manager_school entry
        cm_models.School.objects.get(
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
    model = cm_models.Teacher

    def get_context_data(self, **kwargs):
        context             = super(TeacherListing, self).get_context_data(**kwargs)
        school              = cm_models.School.objects.get(pk=self.kwargs['school_id'])
        context['school']   = school
        context['teachers'] = cm_models.Teacher.objects.filter(school=school)
        context['groups']   = common_util.slug_sort(
            cm_models.StudentGroup.objects.filter(school=school), 'name')
        return context


class TeacherDetail(common_mixins.SchoolEmployeeMixin, DetailView):
    model = cm_models.Teacher

    def get_context_data(self, **kwargs):
        context           = super(TeacherDetail, self).get_context_data(**kwargs)
        context['school'] = cm_models.School.objects.get(pk=self.kwargs['school_id'])
        context['groups'] = common_util.slug_sort(
            cm_models.StudentGroup.objects.filter(
                group_managers = cm_models.Teacher.objects.filter(
                    user = self.request.user)
            ), 'name'
        )
        return context


class TeacherOverview(UserPassesTestMixin, DetailView):
    model = cm_models.Teacher

    def test_func(self):
        try:
            if self.request.user.id == cm_models.Teacher.objects.get(
                pk=self.kwargs['pk']
            ).user.id:
                return True
        except:
            return False
        return False

    def get_context_data(self, **kwargs):
        context           = super(TeacherOverview, self).get_context_data(**kwargs)
        context['school'] = cm_models.School.objects.filter(
            teachers=cm_models.Teacher.objects.filter(
                pk=self.kwargs['pk']
            )
        ).first()
        return context


class TeacherCreate(common_mixins.SchoolManagerMixin, CreateView):
    model      = cm_models.Teacher
    form_class = cm_models.TeacherForm

    def get_context_data(self, **kwargs):
        context           = super(TeacherCreate, self).get_context_data(**kwargs)
        context['school'] = cm_models.School.objects.get(pk=self.kwargs['school_id'])
        return context

    def post(self, *args, **kwargs):
        self.object = cm_models.Teacher.objects.filter(
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
            cm_models.School.objects.get(pk=school_id).teachers.add(self.object)
            return reverse_lazy(
                'schools:school_detail',
                kwargs={'pk': school_id}
            )
        except:
            return reverse_lazy('schools:school_listing')


class TeacherCreateImport(common_mixins.SchoolManagerMixin, CreateView):
    model         = cm_models.Teacher
    form_class    = cm_models.TeacherForm
    template_name = "common/teacher_form_import.html"

    def get_context_data(self, **kwargs):
        # xxx will be available in the template as the related objects
        context           = super(TeacherCreateImport, self).get_context_data(**kwargs)
        context['school'] = cm_models.School.objects.get(pk=self.kwargs['school_id'])
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
                    'school': cm_models.School.objects.get(pk=self.kwargs['school_id'])
                }
            )
        else:
            teacher_data = json.loads(self.request.POST['teachers'])
            # iterate through teachers, add them if they don't exist then add to school
            for teacher in teacher_data:
                try:
                    u, c = User.objects.get_or_create(username=teacher['ssn'])
                    t, c = cm_models.Teacher.objects.get_or_create(
                        ssn=teacher['ssn'], name=teacher['name'], user=u)
                    cm_models.School.objects.get(pk=self.kwargs['school_id']).teachers.add(t)
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
    model      = cm_models.Teacher
    form_class = cm_models.TeacherForm

    def get_context_data(self, **kwargs):
        context           = super(TeacherUpdate, self).get_context_data(**kwargs)
        context['school'] = cm_models.School.objects.get(pk=self.kwargs['school_id'])
        return context

    def post(self, request, **kwargs):
        # get Teacher to be updated
        self.object = cm_models.Teacher.objects.get(pk=self.kwargs['pk'])
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
    model         = cm_models.Teacher
    template_name = "schools/confirm_delete.html"

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        # delete teacher_school entry
        cm_models.School.objects.get(
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
    model = cm_models.Student

    def get_context_data(self, **kwargs):
        context = super(StudentListing, self).get_context_data(**kwargs)
        school  = cm_models.School.objects.get(pk=self.kwargs['school_id'])

        context['school']   = school
        context['students'] = common_util.slug_sort(
            cm_models.Student.objects.filter(school=school), 'name')
        context['students_outside_groups'] = common_util.slug_sort(
            cm_models.Student.objects.filter(school=school).exclude(
                studentgroup__in=cm_models.StudentGroup.objects.filter(school=school)
            ), 'name')
        return context


class StudentDetail(common_mixins.SchoolEmployeeMixin, DetailView):
    model = cm_models.Student

    def get_context_data(self, **kwargs):
        # xxx will be available in the template as the related objects
        context                     = super(StudentDetail, self).get_context_data(**kwargs)
        context['school']           = cm_models.School.objects.get(pk=self.kwargs['school_id'])
        context['student_moreinfo'] = sae_models.StudentExceptionSupport.objects.filter(
            student=self.kwargs.get('pk')).get
        return context


def StudentNotes(request, school_id, pk):
    if request.method == 'POST':
        notes = request.POST.get('notes')
        if (sae_models.StudentExceptionSupport.objects.filter(
            student = cm_models.Student.objects.get(pk=int(pk))
        ).exists()):
            sae_models.StudentExceptionSupport.objects.filter(
                student = cm_models.Student.objects.get(pk=int(pk))).update(notes=notes)
        else:
            ses         = sae_models.StudentExceptionSupport(notes=notes)
            ses.student = cm_models.Student.objects.get(pk=int(pk))
            ses.save()
        return JsonResponse({"message": "success"})


class StudentCreateImport(common_mixins.SchoolManagerMixin, CreateView):
    model         = cm_models.Student
    form_class    = cm_models.StudentForm
    template_name = "common/student_form_import.html"

    def get_context_data(self, **kwargs):
        # xxx will be available in the template as the related objects
        context           = super(StudentCreateImport, self).get_context_data(**kwargs)
        context['school'] = cm_models.School.objects.get(pk=self.kwargs['school_id'])
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
                    'school': cm_models.School.objects.get(pk=self.kwargs['school_id'])
                }
            )
        else:
            student_data = json.loads(self.request.POST['students'])
            school       = cm_models.School.objects.get(pk=self.kwargs['school_id'])
            # iterate through students, add them if they don't exist then add to school
            for data in student_data:
                student = None
                try:
                    student = cm_models.Student.objects.create(**data)
                except:
                    student = cm_models.Student.objects.get(ssn=data['ssn'])
                school.students.add(student)

        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        try:
            school_id = self.kwargs['school_id']
            cm_models.School.objects.get(pk=school_id).students.add(self.object)
            return reverse_lazy(
                'schools:school_detail',
                kwargs={'pk': school_id}
            )
        except:
            return reverse_lazy('schools:school_listing')


class StudentCreate(common_mixins.SchoolManagerMixin, CreateView):
    model      = cm_models.Student
    form_class = cm_models.StudentForm

    def post(self, *args, **kwargs):
        self.object = cm_models.Student.objects.filter(ssn=self.request.POST.get('ssn')).first()
        if self.object:
            return HttpResponseRedirect(self.get_success_url())
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
        context['school'] = cm_models.School.objects.get(pk=self.kwargs['school_id'])
        return context

    def get_success_url(self):
        try:
            school_id = self.kwargs['school_id']
            cm_models.School.objects.get(pk=school_id).students.add(self.object)
            return reverse_lazy(
                'schools:school_detail',
                kwargs={'pk': school_id}
            )
        except:
            return reverse_lazy('schools:school_listing')


class StudentUpdate(common_mixins.SchoolManagerMixin, UpdateView):
    model      = cm_models.Student
    form_class = cm_models.StudentForm

    def get_context_data(self, **kwargs):
        context           = super(StudentUpdate, self).get_context_data(**kwargs)
        context['school'] = cm_models.School.objects.get(pk=self.kwargs['school_id'])
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
    model         = cm_models.Student
    template_name = "schools/confirm_delete.html"

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        # delete student_school entry
        cm_models.School.objects.get(
            pk=self.kwargs.get('school_id')
        ).students.remove(self.object)
        # remove student from all studentgroups in school
        for group in cm_models.StudentGroup.objects.filter(school=self.kwargs.get('school_id')):
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
    model = cm_models.StudentGroup

    def get_context_data(self, **kwargs):
        context                  = super(StudentGroupListing, self).get_context_data(**kwargs)
        school                   = cm_models.School.objects.get(pk=self.kwargs['school_id'])
        context['school']        = school
        context['studentgroups'] = common_util.slug_sort(
            cm_models.StudentGroup.objects.filter(school=school), 'name')
        return context


class StudentGroupDetail(common_mixins.SchoolEmployeeMixin, DetailView):
    model = cm_models.StudentGroup

    def get_context_data(self, **kwargs):
        # xxx will be available in the template as the related objects
        context                = super(StudentGroupDetail, self).get_context_data(**kwargs)
        context['school']      = cm_models.School.objects.get(pk=self.kwargs['school_id'])
        context['exceptions']  = sae_models.Exceptions.objects.all()
        context['supports']    = sae_models.SupportResource.objects.all()
        context['surveys']     = self.object.survey_set.filter(active_to__gte=datetime.now())
        context['old_surveys'] = self.object.survey_set.filter(active_to__lt=datetime.now())
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

        surveys = cm_models.Survey.objects.filter(title=survey_title)
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
    model         = cm_models.StudentGroup
    template_name = "common/studentgroup_admin_list.html"

    def get_context_data(self, **kwargs):
        try:
            context            = super(StudentGroupAdminListing, self).get_context_data(**kwargs)
            context['schools'] = common_util.slug_sort(cm_models.School.objects.all(), 'name')
            context['surveys'] = cm_models.Survey.objects.filter(title=self.kwargs['survey_title'])
        except Exception as e:
            context['error'] = str(e)
        return context


class StudentGroupCreate(common_mixins.SchoolEmployeeMixin, CreateView):
    model = cm_models.StudentGroup
    form_class = cm_models.StudentGroupForm

    def get_context_data(self, **kwargs):
        # xxx will be available in the template as the related objects
        context             = super(StudentGroupCreate, self).get_context_data(**kwargs)
        context['school']   = cm_models.School.objects.get(pk=self.kwargs['school_id'])
        context['students'] = common_util.slug_sort(
            cm_models.Student.objects.filter(school=self.kwargs['school_id']), 'name')
        context['teachers'] = common_util.slug_sort(
            cm_models.Teacher.objects.filter(school=self.kwargs['school_id']), 'name')

        return context

    def post(self, request, *args, **kwargs):
        self.object         = None
        form                = self.get_form()
        # make data mutable
        form.data           = self.request.POST.copy()
        form.data['school'] = cm_models.School.objects.get(pk=self.kwargs['school_id']).pk
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
    model      = cm_models.StudentGroup
    form_class = cm_models.StudentGroupForm

    def get_context_data(self, **kwargs):
        # xxx will be available in the template as the related objects
        context                   = super(StudentGroupUpdate, self).get_context_data(**kwargs)
        context['school']         = cm_models.School.objects.get(pk=self.kwargs['school_id'])
        context['students']       = common_util.slug_sort(
            cm_models.Student.objects.filter(school=self.kwargs['school_id']), 'name')
        context['teachers']       = common_util.slug_sort(
            cm_models.Teacher.objects.filter(school=self.kwargs['school_id']), 'name')
        context['group_managers'] = cm_models.Teacher.objects.filter(studentgroup=self.kwargs['pk'])
        return context

    def post(self, request, *args, **kwargs):
        self.object         = None
        form                = self.get_form()
        # make data mutable
        form.data           = self.request.POST.copy()
        form.data['school'] = cm_models.School.objects.get(pk=self.kwargs['school_id']).pk
        form                = cm_models.StudentGroupForm(
            form.data or None,
            instance = cm_models.StudentGroup.objects.get(id=self.kwargs['pk'])
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
    model         = cm_models.StudentGroup
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
    model = cm_models.Survey

    def get_context_data(self, **kwargs):
        # xxx will be available in the template as the related objects
        context                       = super(SurveyListing, self).get_context_data(**kwargs)
        school                        = cm_models.School.objects.get(pk=self.kwargs['school_id'])
        context['surveylisting_list'] = common_util.slug_sort(cm_models.Survey.objects.filter(
            studentgroup__in = school.object.studentgroup_set.all()
        ), 'title')
        return context


class SurveyAdminListing(common_mixins.SuperUserMixin, ListView):
    model         = cm_models.Survey
    template_name = "common/survey_admin_list.html"

    def get_context_data(self, **kwargs):
        # xxx will be available in the template as the related objects
        try:
            context            = super(SurveyAdminListing, self).get_context_data(**kwargs)
            context['surveys'] = cm_models.Survey.objects.values('title').distinct()
        except Exception as e:
            context['error'] = str(e)
        return context


class SurveyDetail(common_mixins.SchoolEmployeeMixin, DetailView):
    model = cm_models.Survey

    def get_survey_data(self):
        """Get survey details"""
        try:
                uri_list = settings.PROFAGRUNNUR_URL.split('?')
                r        = requests.get(
                    '{0}/{1}?{2}&json_api_key={3}'.format(
                        uri_list[0],
                        self.object.survey,
                        uri_list[1],
                        settings.PROFAGRUNNUR_JSON_KEY
                    )
                )
                return r.json()
        except Exception as e:
            return []

    def get_context_data(self, **kwargs):
        # xxx will be available in the template as the related objects
        context = super(SurveyDetail, self).get_context_data(**kwargs)
        data    = self.get_survey_data()
        if data:
            context['survey_details'] = self.get_survey_data()[0]
        else:
            context['survey_details'] = ''
        context['school']   = cm_models.School.objects.get(pk=self.kwargs['school_id'])
        context['students'] = self.object.studentgroup.students.all()
        context['expired']  = True if self.object.active_to < date.today() else False
        student_results     = {}
        for student in context['students']:
            sr = cm_models.SurveyResult.objects.filter(student=student, survey=self.object)
            if sr:
                r = literal_eval(sr.first().results)  # get student results
                try:
                    student_results[student] = common_util.calc_survey_results(
                        self.object.identifier, literal_eval(r['click_values']), r['input_values'])
                except Exception as e:
                    student_results[student] = common_util.calc_survey_results(
                        self.object.identifier, [], r['input_values'])
            else:
                student_results[student] = common_util.calc_survey_results(
                    self.object.identifier, [], {})
        context['student_results'] = student_results
        context['field_types']     = ['text', 'number', 'text-list', 'number-list']
        return context


class SurveyCreate(common_mixins.SchoolEmployeeMixin, CreateView):
    model      = cm_models.Survey
    form_class = cm_models.SurveyForm

    def get_survey(self):
        """Get all surveys from profagrunnur to provide a list to survey create"""
        try:
                r = requests.get(
                    settings.PROFAGRUNNUR_URL + '&json_api_key=' + settings.PROFAGRUNNUR_JSON_KEY)
                return r.json()
        except Exception as e:
            return []

    def post(self, *args, **kwargs):
        self.object               = None
        form                      = self.get_form()
        # make data mutable
        form.data                 = self.request.POST.copy()
        form.data['studentgroup'] = cm_models.StudentGroup.objects.filter(
            pk=self.kwargs['student_group'])
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def get_context_data(self, **kwargs):
            # xxx will be available in the template as the related objects
            context                = super(SurveyCreate, self).get_context_data(**kwargs)
            context['survey_list'] = self.get_survey()
            return context

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
    model      = cm_models.Survey
    form_class = cm_models.SurveyForm

    def get_survey(self):
        try:
            r = requests.get(
                settings.PROFAGRUNNUR_URL + '&json_api_key=' + settings.PROFAGRUNNUR_JSON_KEY)
            return r.json()
        except Exception as e:
            return []

    def get_form(self):
        form                                 = super(SurveyUpdate, self).get_form(self.form_class)
        form.fields['studentgroup'].queryset = cm_models.StudentGroup.objects.filter(
            school=self.kwargs['school_id'])
        return form

    def get_context_data(self, **kwargs):
            # xxx will be available in the template as the related objects
            context                = super(SurveyUpdate, self).get_context_data(**kwargs)
            context['survey_list'] = self.get_survey()
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
    model         = cm_models.Survey
    template_name = "schools/confirm_delete.html"

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        success_url = self.get_success_url()
        # delete SurveyResults
        cm_models.SurveyResult.objects.filter(survey=self.object).delete()
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


def get_survey_data(kwargs):
    """Get survey details"""
    try:
        survey   = cm_models.Survey.objects.get(pk=kwargs['survey_id']).survey
        uri_list = settings.PROFAGRUNNUR_URL.split('?')
        r        = requests.get(
            '{0}/{1}?{2}&json_api_key={3}'.format(
                uri_list[0],
                survey,
                uri_list[1],
                settings.PROFAGRUNNUR_JSON_KEY
            )
        )
        return r.json()
    except Exception as e:
        return []


class SurveyResultCreate(common_mixins.SchoolEmployeeMixin, CreateView):
    model      = cm_models.SurveyResult
    form_class = cm_models.SurveyResultForm

    def get_context_data(self, **kwargs):
        # xxx will be available in the template as the related objects
        context                = super(SurveyResultCreate, self).get_context_data(**kwargs)
        context['data_result'] = "''"
        context['student']     = cm_models.Student.objects.filter(pk=self.kwargs['student_id'])
        context['survey']      = cm_models.Survey.objects.filter(pk=self.kwargs['survey_id'])
        try:
            data = get_survey_data(self.kwargs)
            if len(data) == 0:
                # survey is expired
                context['grading_template'] = ""
                context['info']             = ""
                context['input_fields']     = ""
            else:
                context['grading_template'] = data[0]['grading_template'][0]['md']
                context['info']             = data[0]['grading_template'][0]['info']
                context['input_fields']     = data[0]['input_fields']
        except Exception as e:
            raise Exception("Ekki næst samband við prófagrunn")
        return context

    def post(self, *args, **kwargs):
        self.object          = None
        form                 = self.get_form()
        # make data mutable
        form.data            = self.request.POST.copy()
        form.data['student'] = cm_models.Student.objects.get(pk=self.kwargs['student_id']).pk
        form.data['survey']  = cm_models.Survey.objects.get(pk=self.kwargs['survey_id']).pk
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        survey_results             = form.save(commit=False)
        survey_results.reported_by = cm_models.Teacher.objects.get(user_id=self.request.user.pk)
        survey_results.student     = cm_models.Student.objects.get(pk=self.kwargs['student_id'])
        survey_results.survey      = cm_models.Survey.objects.get(pk=self.kwargs['survey_id'])
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
            return reverse_lazy(
                'schools:survey_detail',
                kwargs={
                    'pk'       : self.kwargs['survey_id'],
                    'school_id': self.kwargs['school_id']
                }
            )
        except:
            return reverse_lazy('schools:school_listing')


class SurveyResultUpdate(common_mixins.SchoolEmployeeMixin, UpdateView):
    model      = cm_models.SurveyResult
    form_class = cm_models.SurveyResultForm

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
        context['student']          = cm_models.Student.objects.filter(pk=self.kwargs['student_id'])
        context['survey']           = cm_models.Survey.objects.filter(pk=self.kwargs['survey_id'])
        context['data_result']      = json.loads(
            cm_models.SurveyResult.objects.get(pk=self.kwargs['pk']).results
        ) or "''"
        data                        = get_survey_data(self.kwargs)
        context['grading_template'] = data[0]['grading_template'][0]['md']
        context['input_fields']     = data[0]['input_fields']

        return context

    def get_success_url(self):
        try:
            return reverse_lazy(
                'schools:survey_detail',
                kwargs={
                    'pk'       : self.kwargs['survey_id'],
                    'school_id': self.kwargs['school_id']
                }
            )
        except:
            return reverse_lazy('schools:school_listing')


class SurveyResultDelete(common_mixins.SchoolEmployeeMixin, DeleteView):
    model         = cm_models.SurveyResult
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
    model = cm_models.SurveyLogin

    def get_context_data(self, **kwargs):
        # xxx will be available in the template as the related objects
        context                      = super(SurveyLoginListing, self).get_context_data(**kwargs)
        school                       = cm_models.School.objects.get(pk=self.kwargs['school_id'])
        context['school_id']         = school.id
        context['survey_login_list'] = cm_models.SurveyLogin.objects.filter(
            student__in = cm_models.Student.objects.filter(school=school)
        ).values('survey_id').distinct()
        return context


class SurveyLoginAdminListing(common_mixins.SuperUserMixin, ListView):
    model = cm_models.SurveyLogin
    template_name = "common/surveylogin_admin_list.html"
    # Success url?

    def get_context_data(self, **kwargs):
        # xxx will be available in the template as the related objects
        context = super(SurveyLoginAdminListing, self).get_context_data(**kwargs)

        context['survey_login_list'] = cm_models.SurveyLogin.objects.all(
        ).values('survey_id').distinct()
        return context


class SurveyLoginDetail(common_mixins.SchoolManagerMixin, DetailView):
    model = cm_models.SurveyLogin

    def get_object(self, **kwargs):
        return cm_models.SurveyLogin.objects.filter(survey_id=self.kwargs['survey_id']).first()

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
        if 'school_id' in self.kwargs:
            school = cm_models.School.objects.get(pk=self.kwargs['school_id'])

            context['survey_login_students'] = cm_models.SurveyLogin.objects.filter(
                student__in = cm_models.Student.objects.filter(school=school),
                survey_id   = self.kwargs['survey_id']
            )
        else:
            context['survey_login_students'] = cm_models.SurveyLogin.objects.filter(
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
    model         = cm_models.SurveyLogin
    form_class    = cm_models.SurveyLoginForm
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
                student = cm_models.Student.objects.get(ssn=data['ssn'])  # student already exists

                # check if survey_login for student exists, create if not, otherwise update
                survey_login = cm_models.SurveyLogin.objects.filter(
                    student   = student,
                    survey_id = data['survey_id']
                )
                if survey_login:
                    survey_login.update(survey_code=data['password'])
                else:
                    survey_login = cm_models.SurveyLogin.objects.create(
                        student     = student,
                        survey_id   = data['survey_id'],
                        survey_code = data['password']
                    )
        return redirect(self.get_success_url())

    def get_success_url(self):
        return reverse_lazy('schools:survey_login_admin_listing')


class SurveyLoginDelete(common_mixins.SuperUserMixin, DeleteView):
    model         = cm_models.SurveyLogin
    template_name = "schools/confirm_delete.html"

    def get_success_url(self):
        return reverse_lazy('schools:survey_login_admin_listing')

    def get_object(self):
        return cm_models.SurveyLogin.objects.filter(survey_id=self.kwargs['survey_id'])


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
    form_class    = cm_models.SuperUserForm
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
    form_class    = cm_models.SuperUserForm
    template_name = "common/admin_form.html"

    def get_success_url(self):
        return reverse_lazy('schools:admin_listing')


def group_admin_listing_excel(request, survey_title):
    surveys = cm_models.Survey.objects.filter(title=survey_title)

    response                        = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=samræmdupróf.xlsx'
    wb                              = openpyxl.Workbook()

    ws       = wb.get_active_sheet()
    ws.title = 'samræmdupróf'
    ws['A1'] = 'Skóli'
    ws['B1'] = 'Kennitala sḱóla'
    ws['C1'] = 'Nemandi'
    ws['D1'] = 'Kennitala'
    ws['E1'] = 'Bekkur'

    index = 2
    for survey in surveys:

        for student in survey.studentgroup.students.all():
            ws.cell('A' + str(index)).value = survey.studentgroup.school.name
            ws.cell('B' + str(index)).value = survey.studentgroup.school.ssn
            ws.cell('C' + str(index)).value = student.name
            ws.cell('D' + str(index)).value = student.ssn
            ws.cell('E' + str(index)).value = survey.studentgroup.name
            index += 1

    wb.save(response)

    return response


def group_admin_attendance_excel(request, survey_title):

    surveys  = cm_models.Survey.objects.filter(title=survey_title)
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

        for student in survey.studentgroup.students.all():
            ws.cell('A' + str(index)).value = survey.studentgroup.school.name
            ws.cell('B' + str(index)).value = survey.studentgroup.school.ssn
            ws.cell('C' + str(index)).value = student.name
            ws.cell('D' + str(index)).value = student.ssn
            ws.cell('E' + str(index)).value = survey.studentgroup.name

            sr              = cm_models.SurveyResult.objects.filter(student=student, survey=survey)
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
