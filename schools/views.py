# -*- coding: utf-8 -*-
import csv

from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, render_to_response, get_object_or_404, redirect
from django.template import RequestContext, loader
from django.views.generic import ListView, CreateView, DetailView, UpdateView, DeleteView
from django.core.urlresolvers import reverse_lazy, reverse
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.auth.models import User, Group
from django.conf import settings
from django.utils import timezone
from uuid import uuid4
import requests, json
import xlrd
from datetime import datetime

from common.models import *
from supportandexception.models import *
from .util import *

class SchoolListing(ListView):
  model = School

  def get_context_data(self, **kwargs):
    context = super(SchoolListing, self).get_context_data(**kwargs)
    try:
      if self.request.user.is_superuser:
        context['school_list'] = slug_sort(School.objects.all(), 'name')
      else:
        manager_schools = School.objects.filter(managers=Manager.objects.filter(user=self.request.user))
        teacher_schools = School.objects.filter(teachers=Teacher.objects.filter(user=self.request.user))
        context['school_list'] = list(set(slug_sort(manager_schools | teacher_schools, 'name')))
    except Exception as e:
      pass
    return context

class SchoolDetail(UserPassesTestMixin, DetailView):
  model = School

  def get_messages(self):
    """Get all messages from innrivefur"""
    try:
        r = requests.get(settings.INNRI_SKILABOD_URL+'&json_api_key='+settings.INNRI_SKILABOD_JSON_KEY)
        return r.json()
    except Exception as e:
      return []

  def test_func(self):
    return is_school_manager(self.request, self.kwargs) or is_school_teacher(self.request, self.kwargs)

  def get_context_data(self, **kwargs):
    context = super(SchoolDetail, self).get_context_data(**kwargs)
    context['studentgroup_list'] = self.object.studentgroup_set.all()
    context['managers'] = slug_sort(self.object.managers.all(),'name')
    context['teachers'] = slug_sort(self.object.teachers.all(),'name')
    context['surveys'] = slug_sort(Survey.objects.filter(studentgroup__in=self.object.studentgroup_set.all()), 'title')
    context['students'] = self.object.students.all()
    #if self.request.user.id == Manager.objects.get(pk=self.kwargs['pk']).user.id:
    if is_school_teacher(self.request, self.kwargs):
      context['messages'] = [message for message in self.get_messages() if message['teachers_allow'] == True]
    else:
      context['messages'] = self.get_messages()
      
    return context

class SchoolCreate(UserPassesTestMixin, CreateView):
  model = School
  form_class = SchoolForm
  success_url = reverse_lazy('schools:school_listing')
  login_url = reverse_lazy('denied')

  def test_func(self):
    return self.request.user.is_superuser

class SchoolCreateImport(UserPassesTestMixin, CreateView):
  model = School
  form_class = SchoolForm
  login_url = reverse_lazy('denied')
  template_name = "common/school_form_import.html"

  def get_context_data(self, **kwargs):
    # xxx will be available in the template as the related objects
    context = super(SchoolCreateImport, self).get_context_data(**kwargs)
    return context

  def post(self, *args, **kwargs):
    if(self.request.FILES):
      u_file = self.request.FILES['file'].name
      extension = u_file.split(".")[-1]
      ssn = self.request.POST.get('school_ssn')
      name = self.request.POST.get('school_name')
      title = self.request.POST.get('title')
      if title == 'yes':
        first = 1
      else:
        first = 0
      data = []
      if extension == 'csv':
        for row in self.request.FILES['file'].readlines()[first:]:
          row = row.decode('utf-8')
          school_ssn = row.split(',')[int(ssn)]
          school_name = row.split(',')[int(name)]
          data.append({'name': school_name.strip(), 'ssn': school_ssn.strip()})
      elif extension == 'xlsx':
        input_excel = self.request.FILES['file']
        book = xlrd.open_workbook(file_contents=input_excel.read())
        for sheetsnumber in range(book.nsheets):
          sheet = book.sheet_by_index(sheetsnumber)
          for row in range(first, sheet.nrows):
            data.append({'name': sheet.cell_value(row,int(name)), 'ssn': str(int(sheet.cell_value(row,int(ssn))))})

      return render(self.request, 'common/school_verify_import.html', {'data': data})
    else:
      school_data = json.loads(self.request.POST['schools'])
      #iterate through students, add them if they don't exist then add to school
      for school in school_data:
        try:
          s = School.objects.create(**school)
        except:
          pass #student already exists

    return HttpResponseRedirect(self.get_success_url())

  def test_func(self):
    return is_school_manager(self.request, self.kwargs)

  def get_success_url(self):
      return reverse_lazy('schools:school_listing')

class SchoolUpdate(UserPassesTestMixin, UpdateView):
  model = School
  form_class = SchoolForm
  success_url = reverse_lazy('schools:school_listing')
  login_url = reverse_lazy('denied')

  def test_func(self):
    return self.request.user.is_superuser

class SchoolDelete(UserPassesTestMixin, DeleteView):
  model = School
  success_url = reverse_lazy('schools:school_listing')
  login_url = reverse_lazy('denied')
  template_name = "schools/confirm_delete.html"

  def test_func(self):
    return self.request.user.is_superuser

class ManagerListing(UserPassesTestMixin, ListView):
  model = Manager

  def get_context_data(self, **kwargs):
    context = super(ManagerListing, self).get_context_data(**kwargs)
    school = School.objects.get(pk=self.kwargs['school_id'])
    context['school'] = school
    context['managers'] = Manager.objects.filter(school=school)
    return context

  def test_func(self):
    return is_school_manager(self.request, self.kwargs) or is_school_teacher(self.request, self.kwargs)

class ManagerDetail(UserPassesTestMixin, DetailView):
  model = Manager

  def test_func(self):
    return is_school_manager(self.request, self.kwargs) or is_school_teacher(self.request, self.kwargs)

  def get_context_data(self, **kwargs):
    context = super(ManagerDetail, self).get_context_data(**kwargs)
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
    context = super(ManagerOverview, self).get_context_data(**kwargs)
    context['school'] = School.objects.filter(managers=Manager.objects.filter(pk=self.kwargs['pk'])).first()
    return context

class ManagerCreate(UserPassesTestMixin, CreateView):
  model = Manager
  form_class = ManagerForm
  login_url = reverse_lazy('denied')

  def test_func(self):
    return is_school_manager(self.request, self.kwargs)

  def post(self, *args, **kwargs):
    self.object = Manager.objects.filter(name=self.request.POST.get('name')).first()
    if self.object:
      return HttpResponseRedirect(self.get_success_url())
    form = self.get_form()
    #make data mutable
    form.data = self.request.POST.copy()
    #set or create user
    user = User.objects.filter(username=self.request.POST.get('ssn'))
    if user:
      form.data['user'] = user.first().id
    else:
      new_user = User.objects.create(username=self.request.POST.get('ssn'), password=str(uuid4()))
      form.data['user'] = new_user.id
    if form.is_valid():
      return self.form_valid(form)
    else:
      return self.form_invalid(form)

  def get_success_url(self):
    try:
      school_id = self.kwargs['school_id']
      s = School.objects.get(pk=school_id).managers.add(self.object)
      return reverse_lazy('schools:school_detail',
                              kwargs={'pk': school_id})
    except:
      return reverse_lazy('schools:school_listing')

  def get_initial(self):
    school = get_object_or_404(School, pk=self.kwargs.get('school_id'))
    return {
      'school': school,
    }

class ManagerCreateImport(UserPassesTestMixin, CreateView):
  model = School
  form_class = SchoolForm
  login_url = reverse_lazy('denied')
  template_name = "common/manager_form_import.html"

  def get_context_data(self, **kwargs):
    # xxx will be available in the template as the related objects
    context = super(ManagerCreateImport, self).get_context_data(**kwargs)
    return context

  def post(self, *args, **kwargs):
    if(self.request.FILES):
      u_file = self.request.FILES['file'].name
      extension = u_file.split(".")[-1]
      ssn = self.request.POST.get('ssn')
      name = self.request.POST.get('name')
      school_ssn = self.request.POST.get('school_ssn')
      title = self.request.POST.get('title')
      if title == 'yes':
        first = 1
      else:
        first = 0
      data = []
      if extension == 'csv':
        for row in self.request.FILES['file'].readlines()[first:]:
          row = row.decode('utf-8')
          school_ssn = row.split(',')[int(school_ssn)]
          ssn = row.split(',')[ssn]
          name = row.split(',')[name]
          data.append({'name': name.strip(), 
            'ssn': ssn.strip(), 
            'school_ssn': school_ssn.strip()})
      elif extension == 'xlsx':
        input_excel = self.request.FILES['file']
        book = xlrd.open_workbook(file_contents=input_excel.read())
        for sheetsnumber in range(book.nsheets):
          sheet = book.sheet_by_index(sheetsnumber)
          for row in range(first, sheet.nrows):
            data.append({'name': sheet.cell_value(row,int(name)), 
              'ssn': str(int(sheet.cell_value(row,int(ssn)))),
              'school_ssn': str(int(sheet.cell_value(row,int(school_ssn))))})

      return render(self.request, 'common/manager_verify_import.html', {'data': data})
    else:
      manager_data = json.loads(self.request.POST['managers'])
      #iterate through managers, add them if they don't exist then add to school
      for manager in manager_data:
        try:
          m = School.objects.get(ssn=manager['school_ssn']).manager_set.add(**manager)
        except:
          pass #manager already exists

    return HttpResponseRedirect(self.get_success_url())

  def test_func(self):
    return is_school_manager(self.request, self.kwargs)

  def get_success_url(self):
      return reverse_lazy('schools:school_listing')


class ManagerUpdate(UserPassesTestMixin, UpdateView):
  model = Manager
  form_class = ManagerForm
  login_url = reverse_lazy('denied')

  def test_func(self):
    return is_school_manager(self.request, self.kwargs)

  def get_success_url(self):
    try:
      school_id = self.kwargs['school_id']
      return reverse_lazy('schools:school_detail',
                              kwargs={'pk': school_id})
    except:
      return reverse_lazy('schools:school_listing')

class ManagerDelete(UserPassesTestMixin, DeleteView):
  model = Manager
  login_url = reverse_lazy('denied')
  template_name = "schools/confirm_delete.html"

  def test_func(self):
    return is_school_manager(self.request, self.kwargs)

  def delete(self, request, *args, **kwargs):
    self.object = self.get_object()
    #delete manager_school entry
    School.objects.get(pk=self.kwargs.get('school_id')).managers.remove(self.object)
    return HttpResponseRedirect(self.get_success_url())

  def get_success_url(self):
    try:
      return reverse_lazy('schools:school_detail',
                              kwargs={'pk': self.kwargs['school_id']})
    except:
      return reverse_lazy('schools:school_listing')

class TeacherListing(UserPassesTestMixin, ListView):
  model = Teacher

  def get_context_data(self, **kwargs):
    context = super(TeacherListing, self).get_context_data(**kwargs)
    school = School.objects.get(pk=self.kwargs['school_id'])
    context['school'] = school
    context['teachers'] = Teacher.objects.filter(school=school)
    context['groups'] = StudentGroup.objects.filter(school=school)
    print(Teacher.objects.filter(id= StudentGroup.objects.filter(school=school)))
    """context['teachers_in_group'] = Teacher.group_managers.all()"""
    return context

  def test_func(self):
    return is_school_manager(self.request, self.kwargs) or is_school_teacher(self.request, self.kwargs)

class TeacherDetail(UserPassesTestMixin, DetailView):
  model = Teacher

  def test_func(self):
    return is_school_manager(self.request, self.kwargs) or is_school_teacher(self.request, self.kwargs)

  def get_context_data(self, **kwargs):
    context = super(TeacherDetail, self).get_context_data(**kwargs)
    context['school'] = School.objects.get(pk=self.kwargs['school_id'])
    context['groups'] = StudentGroup.objects.filter(group_managers=Teacher.objects.filter(user=self.request.user))
    return context

class TeacherOverview(UserPassesTestMixin, DetailView):
  model = Teacher

  def test_func(self):
    try:
      if self.request.user.id == Teacher.objects.get(pk=self.kwargs['pk']).user.id:
        return True
    except:
      return False
    return False

  def get_context_data(self, **kwargs):
    context = super(TeacherOverview, self).get_context_data(**kwargs)
    context['school'] = School.objects.filter(teachers=Teacher.objects.filter(pk=self.kwargs['pk'])).first()
    return context

class TeacherCreate(UserPassesTestMixin, CreateView):
  model = Teacher
  form_class = TeacherForm
  login_url = reverse_lazy('denied')

  def test_func(self):
    return is_school_manager(self.request, self.kwargs)

  def post(self, *args, **kwargs):
    self.object = Teacher.objects.filter(ssn=self.request.POST.get('ssn')).first()
    if self.object:
      return HttpResponseRedirect(self.get_success_url())
    form = self.get_form()
    #make data mutable
    form.data = self.request.POST.copy()
    #set or create user
    user = User.objects.filter(username=self.request.POST.get('ssn'))

    if user:
      form.data['user'] = user.first().id
    else:
       user = User.objects.create(username=self.request.POST.get('ssn'), password=str(uuid4()))
       form.data['user'] = user.id

    if form.is_valid():
      return self.form_valid(form)
    else:
      return self.form_invalid(form)

  def get_success_url(self):
    try:
      school_id = self.kwargs['school_id']
      School.objects.get(pk=school_id).teachers.add(self.object)
      return reverse_lazy('schools:school_detail',
                              kwargs={'pk': school_id})
    except:
      return reverse_lazy('schools:school_listing')

class TeacherUpdate(UserPassesTestMixin, UpdateView):
  model = Teacher
  form_class = TeacherForm
  login_url = reverse_lazy('denied')

  def test_func(self):
    return is_school_manager(self.request, self.kwargs)

  def get_success_url(self):
    try:
      school_id = self.kwargs['school_id']
      return reverse_lazy('schools:school_detail',
                              kwargs={'pk': school_id})
    except:
      return reverse_lazy('schools:school_listing')

class TeacherDelete(UserPassesTestMixin, DeleteView):
  model = Teacher
  login_url = reverse_lazy('denied')
  template_name = "schools/confirm_delete.html"

  def test_func(self):
    return is_school_manager(self.request, self.kwargs)

  def delete(self, request, *args, **kwargs):
    self.object = self.get_object()
    #delete teacher_school entry
    School.objects.get(pk=self.kwargs.get('school_id')).teachers.remove(self.object)
    return HttpResponseRedirect(self.get_success_url())

  def get_success_url(self):
    try:
      return reverse_lazy('schools:school_detail',
                              kwargs={'pk': self.kwargs['school_id']})
    except:
      return reverse_lazy('schools:school_listing')

class StudentListing(UserPassesTestMixin, ListView):
  model = Student

  def get_context_data(self, **kwargs):
    context = super(StudentListing, self).get_context_data(**kwargs)
    school = School.objects.get(pk=self.kwargs['school_id'])
    context['school'] = school
    context['students'] = slug_sort(Student.objects.filter(school=school), 'name')
    context['students_outside_groups'] = slug_sort(Student.objects.filter(school=school).exclude(studentgroup__in=StudentGroup.objects.filter(school=school)), 'name')
    return context

  def test_func(self):
    return is_school_manager(self.request, self.kwargs) or is_school_teacher(self.request, self.kwargs)

class StudentDetail(UserPassesTestMixin, DetailView):
  model = Student

  def test_func(self):
    return is_school_manager(self.request, self.kwargs) or is_school_teacher(self.request, self.kwargs)

  def get_context_data(self, **kwargs):
    # xxx will be available in the template as the related objects
    context = super(StudentDetail, self).get_context_data(**kwargs)
    context['school'] = School.objects.get(pk=self.kwargs['school_id'])
    context['student_moreinfo'] = StudentExceptionSupport.objects.filter(student=self.kwargs.get('pk')).get
    return context


def StudentNotes(request, school_id, pk):
  if request.method == 'POST':
    notes = request.POST.get('notes')
    if (StudentExceptionSupport.objects.filter(student = Student.objects.get(pk=int(pk))).exists()):
      StudentExceptionSupport.objects.filter(student = Student.objects.get(pk=int(pk))).update(notes=notes)
    else:
      ses = StudentExceptionSupport(notes=notes)
      ses.student = Student.objects.get(pk=int(pk))
      ses.save()
    return JsonResponse({"message": "success"})

class StudentCreateImport(UserPassesTestMixin, CreateView):
  model = Student
  form_class = StudentForm
  login_url = reverse_lazy('denied')
  template_name = "common/student_form_import.html"

  def get_context_data(self, **kwargs):
    # xxx will be available in the template as the related objects
    context = super(StudentCreateImport, self).get_context_data(**kwargs)
    context['school'] = School.objects.get(pk=self.kwargs['school_id'])
    return context

  def post(self, *args, **kwargs):
    if(self.request.FILES):
      u_file = self.request.FILES['file'].name
      extension = u_file.split(".")[-1]
      ssn = self.request.POST.get('student_ssn')
      name = self.request.POST.get('student_name')
      title = self.request.POST.get('title')
      if title == 'yes':
        first = 1
      else:
        first = 0
      data = []
      if extension == 'csv':
        for row in self.request.FILES['file'].readlines()[first:]:
          row = row.decode('utf-8')
          student_ssn = row.split(',')[int(ssn)]
          student_name = row.split(',')[int(name)]
          data.append({'name': student_name.strip(), 'ssn': student_ssn.strip()})
      elif extension == 'xlsx':
        input_excel = self.request.FILES['file']
        book = xlrd.open_workbook(file_contents=input_excel.read())
        for sheetsnumber in range(book.nsheets):
          sheet = book.sheet_by_index(sheetsnumber)
          for row in range(first, sheet.nrows):
            data.append({'name': str(sheet.cell_value(row,int(name))), 'ssn': str(int(sheet.cell_value(row,int(ssn))))})
      return render(self.request, 'common/student_verify_import.html', {'data': data, 'school': School.objects.get(pk=self.kwargs['school_id'])})
    else:
      student_data = json.loads(self.request.POST['students'])
      school = School.objects.get(pk=self.kwargs['school_id'])
      #iterate through students, add them if they don't exist then add to school
      for data in student_data:
        student = None
        try:
          student = Student.objects.create(**data)
        except:
          student = Student.objects.get(ssn=data['ssn'])
        school.students.add(student)

    return HttpResponseRedirect(self.get_success_url())

  def test_func(self):
    return is_school_manager(self.request, self.kwargs)

  def get_success_url(self):
    try:
      school_id = self.kwargs['school_id']
      School.objects.get(pk=school_id).students.add(self.object)
      return reverse_lazy('schools:school_detail',
                              kwargs={'pk': school_id})
    except:
      return reverse_lazy('schools:school_listing')

class StudentCreate(UserPassesTestMixin, CreateView):
  model = Student
  form_class = StudentForm
  login_url = reverse_lazy('denied')

  def test_func(self):
    return is_school_manager(self.request, self.kwargs)

  def post(self, *args, **kwargs):
    self.object = Student.objects.filter(ssn=self.request.POST.get('ssn')).first()
    if self.object:
      return HttpResponseRedirect(self.get_success_url())
    form = self.get_form()
    #make data mutable
    form.data = self.request.POST.copy()
    #set or create user
    user = User.objects.filter(username=self.request.POST.get('ssn'))
    if user:
      form.data['user'] = user
    else:
      form.data['user'] = User.objects.create(username=self.request.POST.get('ssn'), password=str(uuid4()))

    if form.is_valid():
      return self.form_valid(form)
    else:
      return self.form_invalid(form)

  def get_success_url(self):
    try:
      school_id = self.kwargs['school_id']
      School.objects.get(pk=school_id).students.add(self.object)
      return reverse_lazy('schools:school_detail',
                              kwargs={'pk': school_id})
    except:
      return reverse_lazy('schools:school_listing')

class StudentUpdate(UserPassesTestMixin, UpdateView):
  model = Student
  form_class = StudentForm
  login_url = reverse_lazy('denied')

  def test_func(self):
    return is_school_manager(self.request, self.kwargs)

  def get_success_url(self):
    try:
      school_id = self.kwargs['school_id']
      return reverse_lazy('schools:school_detail',
                              kwargs={'pk': school_id})
    except:
      return reverse_lazy('schools:school_listing')

class StudentDelete(UserPassesTestMixin, DeleteView):
  model = Student
  login_url = reverse_lazy('denied')
  template_name = "schools/confirm_delete.html"

  def test_func(self):
    return is_school_manager(self.request, self.kwargs)

  def delete(self, request, *args, **kwargs):
    self.object = self.get_object()
    #delete student_school entry
    School.objects.get(pk=self.kwargs.get('school_id')).students.remove(self.object)
    return HttpResponseRedirect(self.get_success_url())

  def get_success_url(self):
    try:
      school_id = self.kwargs['school_id']
      return reverse_lazy('schools:school_detail',
                              kwargs={'pk': school_id})
    except:
      return reverse_lazy('schools:school_listing')

class StudentGroupListing(UserPassesTestMixin, ListView):
  model = StudentGroup

  def get_context_data(self, **kwargs):
    context = super(StudentGroupListing, self).get_context_data(**kwargs)
    school = School.objects.get(pk=self.kwargs['school_id'])
    context['school'] = school
    context['studentgroups'] = slug_sort(StudentGroup.objects.filter(school=school), 'name')
    return context

  def test_func(self):
    return is_school_manager(self.request, self.kwargs) or is_school_teacher(self.request, self.kwargs)

class StudentGroupDetail(UserPassesTestMixin, DetailView):
  model = StudentGroup

  def test_func(self):
    return is_school_manager(self.request, self.kwargs) or is_school_teacher(self.request, self.kwargs)

  def get_context_data(self, **kwargs):
    # xxx will be available in the template as the related objects
    context = super(StudentGroupDetail, self).get_context_data(**kwargs)
    context['school'] = School.objects.get(pk=self.kwargs['school_id'])
    context['exceptions'] = Exceptions.objects.all()
    context['supports'] = SupportResource.objects.all()
    context['surveys'] = self.object.survey_set.filter(active_to__gte=datetime.now())
    context['old_surveys'] = self.object.survey_set.filter(active_to__lt=datetime.now())
    return context

class StudentGroupCreate(UserPassesTestMixin, CreateView):
  model = StudentGroup
  form_class = StudentGroupForm
  login_url = reverse_lazy('denied')

  def get_context_data(self, **kwargs):
    # xxx will be available in the template as the related objects
    context = super(StudentGroupCreate, self).get_context_data(**kwargs)
    context['school'] = School.objects.get(pk=self.kwargs['school_id'])
    context['students'] = slug_sort(Student.objects.filter(school=self.kwargs['school_id']), 'name')
    context['teachers'] = slug_sort(Teacher.objects.filter(school=self.kwargs['school_id']), 'name')

    return context

  def post(self, request, *args, **kwargs):
    self.object = None
    form = self.get_form()
    #make data mutable
    form.data = self.request.POST.copy()
    form.data['school'] = School.objects.get(pk=self.kwargs['school_id']).pk
    if form.is_valid():
      return self.form_valid(form)
    else:
      return self.form_invalid(form)

  def test_func(self):
    return is_school_manager(self.request, self.kwargs) or is_school_teacher(self.request, self.kwargs)

  def get_success_url(self):
    try:
      school_id = self.kwargs['school_id']
      return reverse_lazy('schools:school_detail',
                              kwargs={'pk': school_id})
    except:
      return reverse_lazy('schools:school_listing')


class StudentGroupUpdate(UserPassesTestMixin, UpdateView):
  model = StudentGroup
  form_class = StudentGroupForm
  login_url = reverse_lazy('denied')


  def get_context_data(self, **kwargs):
    # xxx will be available in the template as the related objects
    context = super(StudentGroupUpdate, self).get_context_data(**kwargs)
    #context['contact_list'] = Contact.objects.filter(school=self.get_object())
    school = School.objects.get(pk=self.kwargs['school_id'])
    context['school'] = School.objects.get(pk=self.kwargs['school_id'])
    context['students'] = slug_sort(Student.objects.filter(school=self.kwargs['school_id']), 'name')
    context['teachers'] = slug_sort(Teacher.objects.filter(school=self.kwargs['school_id']), 'name')
    context['group_managers'] = Teacher.objects.filter(studentgroup=self.kwargs['pk'])
    return context

  def post(self, request, *args, **kwargs):
    self.object = None
    form = self.get_form()
    #make data mutable
    form.data = self.request.POST.copy()
    form.data['school'] = School.objects.get(pk=self.kwargs['school_id']).pk
    form = StudentGroupForm(form.data or None, instance = StudentGroup.objects.get(id=self.kwargs['pk']))
    if form.is_valid():
      form.save()
      return self.form_valid(form)
    else:
      return self.form_invalid(form)

  def test_func(self):
    return is_school_manager(self.request, self.kwargs) or is_school_teacher(self.request, self.kwargs) #TODO: manager or (teacher and group_manager)

  def get_success_url(self):
    try:
      school_id = self.kwargs['school_id']
      return reverse_lazy('schools:group_detail',
                              kwargs={'school_id': school_id, 'pk': self.kwargs['pk']})
    except:
      return reverse_lazy('schools:school_listing')




class StudentGroupDelete(UserPassesTestMixin, DeleteView):
  model = StudentGroup
  login_url = reverse_lazy('denied')
  template_name = "schools/confirm_delete.html"

  def test_func(self):
    return is_school_manager(self.request, self.kwargs) or is_school_teacher(self.request, self.kwargs) #TODO: manager or (teacher and group_manager)

  def get_success_url(self):
    try:
      school_id = self.kwargs['school_id']
      return reverse_lazy('schools:school_detail',
                              kwargs={'pk': school_id})
    except:
      return reverse_lazy('schools:school_listing')

class SurveyListing(UserPassesTestMixin, ListView):
  model = Survey

  def get_context_data(self, **kwargs):
    # xxx will be available in the template as the related objects
    context = super(SurveyListing, self).get_context_data(**kwargs)
    school = School.objects.get(pk=self.kwargs['school_id'])
    context['surveylisting_list'] = slug_sort(Survey.objects.filter(studentgroup__in=school.object.studentgroup_set.all()), 'title')
    return context

  def test_func(self):
    return is_school_manager(self.request, self.kwargs) or is_school_teacher(self.request, self.kwargs)

class SurveyDetail(UserPassesTestMixin, DetailView):
  model = Survey

  def get_survey_data(self):
    """Get survey details"""
    try:
        uri_list = settings.PROFAGRUNNUR_URL.split('?')
        r = requests.get(''.join([uri_list[0], '/', self.object.survey, '?', uri_list[1], '&json_api_key=',settings.PROFAGRUNNUR_JSON_KEY]))
        return r.json()
    except Exception as e:
      return []

  def test_func(self):
    return is_school_manager(self.request, self.kwargs) or is_school_teacher(self.request, self.kwargs)

  def get_context_data(self, **kwargs):
    # xxx will be available in the template as the related objects
    context = super(SurveyDetail, self).get_context_data(**kwargs)
    data = self.get_survey_data()
    if data:
      context['survey_details'] = self.get_survey_data()[0]
    else:
      context['survey_details'] = ''
    context['school'] = School.objects.get(pk=self.kwargs['school_id'])
    context['students'] = self.object.studentgroup.students.all()
    context['field_types'] = ['text', 'number', 'text-list', 'number-list']
    return context

class SurveyCreate(UserPassesTestMixin, CreateView):
  model = Survey
  form_class = SurveyForm
  login_url = reverse_lazy('denied')

  def get_survey(self):
    """Get all surveys from profagrunnur to provide a list to survey create"""
    try:
        r = requests.get(settings.PROFAGRUNNUR_URL+'&json_api_key='+settings.PROFAGRUNNUR_JSON_KEY)
        return r.json()
    except Exception as e:
      return []

  def post(self, *args, **kwargs):
    self.object = None
    form = self.get_form()
    #make data mutable
    form.data = self.request.POST.copy()
    form.data['studentgroup'] = StudentGroup.objects.filter(pk=self.kwargs['student_group'])
    if form.is_valid():
      return self.form_valid(form)
    else:
      return self.form_invalid(form)

  def get_context_data(self, **kwargs):
      # xxx will be available in the template as the related objects
      context = super(SurveyCreate, self).get_context_data(**kwargs)
      context['survey_list'] = self.get_survey()
      return context

  def test_func(self):
    return is_group_manager(self.request, self.kwargs) or is_school_manager(self.request, self.kwargs) #TODO: manager or (teacher and group_manager)

  def get_success_url(self):
    try:
      school_id = self.kwargs['school_id']
      student_group = self.kwargs['student_group']
      return reverse_lazy('schools:group_detail',
                              kwargs={'school_id': school_id, 'pk': student_group})
    except:
      return reverse_lazy('schools:school_listing')

class SurveyUpdate(UserPassesTestMixin, UpdateView):
  model = Survey
  form_class = SurveyForm
  login_url = reverse_lazy('denied')

  def test_func(self):
    return is_school_manager(self.request, self.kwargs) or is_school_teacher(self.request, self.kwargs) #TODO: manager or (teacher and group_manager)

  def get_survey(self):
    try:
        r = requests.get(settings.PROFAGRUNNUR_URL+'&json_api_key='+settings.PROFAGRUNNUR_JSON_KEY)
        return r.json()
    except Exception as e:
      return []

  def get_form(self):
    form = super(SurveyUpdate, self).get_form(self.form_class)
    form.fields['studentgroup'].queryset = StudentGroup.objects.filter(school=self.kwargs['school_id'])
    return form

  def get_context_data(self, **kwargs):
      # xxx will be available in the template as the related objects
      context = super(SurveyUpdate, self).get_context_data(**kwargs)
      context['survey_list'] = self.get_survey()
      return context

  def get_success_url(self):
    try:
      school_id = self.kwargs['school_id']
      return reverse_lazy('schools:school_detail',
                              kwargs={'pk': school_id})
    except:
      return reverse_lazy('schools:school_listing')

class SurveyDelete(UserPassesTestMixin, DeleteView):
  model = Survey
  login_url = reverse_lazy('denied')
  template_name = "schools/confirm_delete.html"

  def test_func(self):
    return is_school_manager(self.request, self.kwargs) or is_school_teacher(self.request, self.kwargs) #TODO: manager or (teacher and group_manager)

  def delete(self, request, *args, **kwargs):
    self.object = self.get_object()
    success_url = self.get_success_url()
    #delete SurveyResults
    SurveyResult.objects.filter(survey=self.object).delete()
    self.object.delete()
    return HttpResponseRedirect(success_url)

  def get_success_url(self):
    try:
      school_id = self.kwargs['school_id']
      return reverse_lazy('schools:school_detail',
                              kwargs={'pk': school_id})
    except:
      return reverse_lazy('schools:school_listing')

def get_survey_data(kwargs):
  """Get survey details"""
  try:
    survey = Survey.objects.get(pk=kwargs['survey_id']).survey
    uri_list = settings.PROFAGRUNNUR_URL.split('?')
    r = requests.get(''.join([uri_list[0], '/', survey, '?', uri_list[1], '&json_api_key=',settings.PROFAGRUNNUR_JSON_KEY]))
    return r.json()
  except Exception as e:
    return []

class SurveyResultCreate(UserPassesTestMixin, CreateView):
  model = SurveyResult
  form_class = SurveyResultForm
  login_url = reverse_lazy('denied')

  def get_context_data(self, **kwargs):
    # xxx will be available in the template as the related objects
    context = super(SurveyResultCreate, self).get_context_data(**kwargs)
    context['data_result'] = "''"
    context['student'] = Student.objects.filter(pk=self.kwargs['student_id'])
    context['survey'] = Survey.objects.filter(pk=self.kwargs['survey_id'])
    data = get_survey_data(self.kwargs)
    try:
      if len(data) == 0:
        #survey is expired
        context['grading_template'] = ""
        context['info'] = ""
      else:
        context['grading_template'] = data[0]['grading_template'][0]['md']
        context['info'] = data[0]['grading_template'][0]['info']
    except Exception as e:
      raise Exception("Ekki næst samband við prófagrunn")
    return context

  def post(self, *args, **kwargs):
    self.object = None
    form = self.get_form()
    #make data mutable
    form.data = self.request.POST.copy()
    form.data['student'] = Student.objects.get(pk=self.kwargs['student_id']).pk
    form.data['survey'] = Survey.objects.get(pk=self.kwargs['survey_id']).pk
    if form.is_valid():
      return self.form_valid(form)
    else:
      return self.form_invalid(form)

  def form_valid(self, form):
    survey_results = form.save(commit=False)
    survey_results.reported_by =Teacher.objects.get(user_id=self.request.user.pk)
    survey_results.student = Student.objects.get(pk=self.kwargs['student_id'])
    survey_results.survey = Survey.objects.get(pk=self.kwargs['survey_id'])
    survey_results.created_at = timezone.now()
    data_results = {}
    #extract data
    survey_results.results = json.dumps(self.request.POST.getlist('data_results[]'))
    return super(SurveyResultCreate, self).form_valid(form)

  def test_func(self):
    return is_group_manager(self.request, self.kwargs)

  def get_success_url(self):
    try:
      return reverse_lazy('schools:survey_detail',
                              kwargs={
                                'pk': self.kwargs['survey_id'],
                                'school_id': self.kwargs['school_id']
                              })
    except:
      return reverse_lazy('schools:school_listing')

class SurveyResultUpdate(UserPassesTestMixin, UpdateView):
  model = SurveyResult
  form_class = SurveyResultForm
  login_url = reverse_lazy('denied')

  def test_func(self):
    return is_school_manager(self.request, self.kwargs) or is_school_teacher(self.request, self.kwargs) #TODO: manager or (teacher and group_manager)

  def form_valid(self, form):
    survey_results = form.save(commit=False)
    survey_results.created_at = timezone.now()
    data_results = {}
    #extract data
    survey_results.results = json.dumps(self.request.POST.getlist('data_results[]'))
    return super(SurveyResultUpdate, self).form_valid(form)

  def get_context_data(self, **kwargs):
    # xxx will be available in the template as the related objects
    context = super(SurveyResultUpdate, self).get_context_data(**kwargs)
    context['student'] = Student.objects.filter(pk=self.kwargs['student_id'])
    context['survey'] = Survey.objects.filter(pk=self.kwargs['survey_id'])
    context['data_result'] = json.loads(SurveyResult.objects.get(pk=self.kwargs['pk']).results) or "''"
    data = get_survey_data(self.kwargs)
    context['grading_template'] = data[0]['grading_template'][0]['md']

    return context

  def get_success_url(self):
    try:
      return reverse_lazy('schools:survey_detail',
                              kwargs={
                                'pk': self.kwargs['survey_id'],
                                'school_id': self.kwargs['school_id']
                              })
    except:
      return reverse_lazy('schools:school_listing')

class SurveyResultDelete(UserPassesTestMixin, DeleteView):
  model = SurveyResult
  login_url = reverse_lazy('denied')
  template_name = "schools/confirm_delete.html"

  def test_func(self):
    return is_school_manager(self.request, self.kwargs) or is_school_teacher(self.request, self.kwargs) #TODO: manager or (teacher and group_manager)

  def get_success_url(self):
    try:
      school_id = self.kwargs['school_id']
      return reverse_lazy('schools:school_detail',
                              kwargs={'pk': school_id})
    except:
      return reverse_lazy('schools:school_listing')

class SurveyLoginListing(UserPassesTestMixin, ListView):
  model = SurveyLogin

  def get_context_data(self, **kwargs):
    # xxx will be available in the template as the related objects
    context = super(SurveyLoginListing, self).get_context_data(**kwargs)
    school = School.objects.get(pk=self.kwargs['school_id'])
    context['school_id'] = school.id
    context['survey_login_list'] = SurveyLogin.objects.filter(student__in = Student.objects.filter(school=school)).values('survey_id').distinct()
    return context

  def test_func(self):
    return is_school_manager(self.request, self.kwargs) or is_school_teacher(self.request, self.kwargs)

class SurveyLoginAdminListing(UserPassesTestMixin, ListView):
  model = SurveyLogin
  template_name = "common/surveylogin_admin_list.html"

  def get_context_data(self, **kwargs):
    # xxx will be available in the template as the related objects
    context = super(SurveyLoginAdminListing, self).get_context_data(**kwargs)
    context['survey_login_list'] = SurveyLogin.objects.all().values('survey_id').distinct()
    return context

  def test_func(self):
    return self.request.user.is_superuser

class SurveyLoginDetail(UserPassesTestMixin, DetailView):
  model = SurveyLogin

  def test_func(self):
    return is_school_manager(self.request, self.kwargs)

  def get_object(self, **kwargs):
    return SurveyLogin.objects.filter(survey_id=self.kwargs['survey_id']).first()

  def get_context_data(self, **kwargs):
    # xxx will be available in the template as the related objects
    context = super(SurveyLoginDetail, self).get_context_data(**kwargs)
    context['survey_id'] = self.kwargs['survey_id']
    if 'school_id' in self.kwargs:
      school = School.objects.get(pk=self.kwargs['school_id'])
      context['survey_login_students'] = SurveyLogin.objects.filter(student__in = Student.objects.filter(school=school)).filter(survey_id=self.kwargs['survey_id'])
    else:
      context['survey_login_students'] = SurveyLogin.objects.filter(survey_id=self.kwargs['survey_id'])
    return context

class SurveyLoginCreate(UserPassesTestMixin, CreateView):
  model = SurveyLogin
  form_class = SurveyLoginForm
  template_name = "common/password_form_import.html"
  login_url = reverse_lazy('denied')

  def post(self, *args, **kwargs):
    if(self.request.FILES):
      u_file = self.request.FILES['file'].name
      extension = u_file.split(".")[-1]
      ssn = self.request.POST.get('student_ssn')
      name = self.request.POST.get('student_name')
      survey_id = self.request.POST.get('survey_id')
      password = self.request.POST.get('password')
      title = self.request.POST.get('title')

      if title == 'yes':
        first = 1
      else:
        first = 0

      data = []
      try:
        if extension == 'csv':
          for row in self.request.FILES['file'].readlines()[first:]:
            row = row.decode('utf-8')
            student_ssn = row.split(',')[int(ssn)]
            student_survey_id = row.split(',')[int(survey_id)]
            student_name = row.split(',')[int(name)]
            student_password = row.split(',')[int(password)]
            data.append({
              'survey_id': student_survey_id.strip(),
              'ssn': student_ssn.strip(),
              'name': student_name.strip(),
              'password': student_password.strip()})
        elif extension == 'xlsx':
          input_excel = self.request.FILES['file']
          book = xlrd.open_workbook(file_contents=input_excel.read())
          for sheetsnumber in range(book.nsheets):
            sheet = book.sheet_by_index(sheetsnumber)
            for row in range(first, sheet.nrows):
              data.append({
                'survey_id': str(sheet.cell_value(row,int(survey_id))),
                'ssn': str(int(sheet.cell_value(row,int(ssn)))),
                'name': str(int(sheet.cell_value(row,int(name)))),
                'password': str(int(sheet.cell_value(row,int(password)))),
                })
        return render(self.request, 'common/password_verify_import.html', {'data': data})
      except Exception as e:
        return render(self.request, 'common/password_form_import.html', {'error': 'Dálkur ekki til, reyndu aftur'})

    else:
      student_data = json.loads(self.request.POST['students'])
      #iterate through the data, add students if they don't exist then create a survey_login object
      for data in student_data:
        student = None
        try:
          student = Student.objects.create(ssn=data['ssn'], name=data['name'])
        except Exception as e:
          student = Student.objects.get(ssn=data['ssn']) #student already exists

        #check if survey_login for student exists, create if not, otherwise update
        survey_login = SurveyLogin.objects.filter(student=student, survey_id=data['survey_id'])
        if survey_login:
          survey_login.update(survey_code=data['password'])
        else:
          survey_login = SurveyLogin.objects.create(student=student, survey_id = data['survey_id'], survey_code=data['password'])
    return redirect(self.get_success_url())

  def get_success_url(self):
    return reverse_lazy('schools:survey_login_admin_listing')

  def test_func(self):
    return self.request.user.is_superuser

class SurveyLoginDelete(UserPassesTestMixin, DeleteView):
  model = SurveyLogin
  login_url = reverse_lazy('denied')
  template_name = "schools/confirm_delete.html"

  def test_func(self):
    return self.request.user.is_superuser

  def get_success_url(self):
    return reverse_lazy('schools:survey_login_admin_listing')

  def get_object(self):
    return SurveyLogin.objects.filter(survey_id=self.kwargs['survey_id'])

class AdminListing(UserPassesTestMixin, ListView):
  model = User
  login_url = reverse_lazy('denied')
  template_name = "common/admin_list.html"

  def test_func(self):
    return self.request.user.is_superuser

  def get_success_url(self):
    return reverse_lazy('schools:admin_listing')

  def get_context_data(self, **kwargs):
    # xxx will be available in the template as the related objects
    context = super(AdminListing, self).get_context_data(**kwargs)
    context['user_list'] = User.objects.filter(is_superuser=True)
    return context

class AdminCreate(UserPassesTestMixin, CreateView):
  model = User
  form_class = SuperUserForm
  login_url = reverse_lazy('denied')
  template_name = "common/admin_form.html"

  def test_func(self):
    return self.request.user.is_superuser

  def post(self, *args, **kwargs):
    username = self.request.POST.get('username')
    is_superuser = self.request.POST.get('is_superuser', False)
    if User.objects.filter(username=username).exists():
      if is_superuser:
        User.objects.filter(username=username).update(is_superuser=True)
    else:
      user = User.objects.create_user(
        username=username,
        is_superuser=is_superuser
      )
    return redirect(self.get_success_url())

  def get_success_url(self):
    return reverse_lazy('schools:admin_listing')

class AdminUpdate(UserPassesTestMixin, UpdateView):
  model = User
  form_class = SuperUserForm
  login_url = reverse_lazy('denied')
  template_name = "common/admin_form.html"

  def test_func(self):
    return self.request.user.is_superuser

  def get_success_url(self):
    return reverse_lazy('schools:admin_listing') 