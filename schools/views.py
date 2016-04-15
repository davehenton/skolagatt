# -*- coding: utf-8 -*-
import csv

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, render_to_response, get_object_or_404
from django.template import RequestContext, loader
from django.views.generic import ListView, CreateView, DetailView, UpdateView, DeleteView
from django.core.urlresolvers import reverse_lazy, reverse
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.auth.models import User, Group
from uuid import uuid4

from common.models import School, Student, StudentGroup, Manager, Teacher
from common.models import SchoolForm, StudentForm, StudentGroupForm, ManagerForm, TeacherForm

class SchoolListing(UserPassesTestMixin, ListView):
  model = School

  def test_func(self):
    return True #is_manager(self.request.user, self.get_object()) or is_teacher(self.request.user, self.get_object())

class SchoolDetail(UserPassesTestMixin, DetailView):
  model = School

  def test_func(self, **kwargs):
    return True #is_manager(self.request.user, self.get_object()) or is_teacher(self.request.user, self.get_object())

  def get_context_data(self, **kwargs):
    context = super(SchoolDetail, self).get_context_data(**kwargs)
    context['studentgroup_list'] = self.object.studentgroup_set.all()
    context['managers'] = self.object.managers.all()
    context['teachers'] = self.object.teachers.all()
    context['students'] = self.object.students.all()
    context['is_teacher'] = not self.request.user.is_anonymous()
    return context

class SchoolCreate(UserPassesTestMixin, CreateView):
  model = School
  form_class = SchoolForm
  success_url = reverse_lazy('schools:school_listing')
  login_url = reverse_lazy('denied')

  def test_func(self):
    return self.request.user.is_superuser

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
    return True # is_manager(self) or is_teacher(self)

class ManagerDetail(UserPassesTestMixin, DetailView):
  model = Manager

  def test_func(self):
    return True #is_manager(self) or is_teacher(self)

  def get_context_data(self, **kwargs):
    context = super(ManagerDetail, self).get_context_data(**kwargs)
    context['is_teacher'] = not self.request.user.is_anonymous()
    context['school'] = School.objects.get(pk=self.kwargs['school_id'])
    return context

class ManagerCreate(UserPassesTestMixin, CreateView):
  model = Manager
  form_class = ManagerForm
  login_url = reverse_lazy('denied')

  def test_func(self, **kwargs):
    return True # is_manager(self) or self.request.user.is_superuser()

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
      new_user = User.objects.create(username=self.request.POST.get('ssn'), password=str(uuid4))
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

class ManagerUpdate(UserPassesTestMixin, UpdateView):
  model = Manager
  form_class = ManagerForm
  login_url = reverse_lazy('denied')

  def test_func(self):
    return True #is_manager(self) or self.request.user.is_superuser()

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
    return True #is_manager(self) or self.request.user.is_superuser()

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
    return context

  def test_func(self):
    return True #is_manager(self) or is_teacher(self)

class TeacherDetail(UserPassesTestMixin, DetailView):
  model = Teacher

  def test_func(self):
    return True #is_manager(self) or is_teacher(self)

  def get_context_data(self, **kwargs):
    context = super(TeacherDetail, self).get_context_data(**kwargs)
    context['school'] = School.objects.get(pk=self.kwargs['school_id'])
    context['is_teacher'] = not self.request.user.is_anonymous()
    return context

class TeacherCreate(UserPassesTestMixin, CreateView):
  model = Teacher
  form_class = TeacherForm
  login_url = reverse_lazy('denied')

  def test_func(self):
    return True #is_manager(self) or self.request.user.is_superuser()

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
      form.data['user'] = user
    else:
      form.data['user'] = User.objects.create(username=self.request.POST.get('ssn'), password=str(uuid4))

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
    return True #is_manager(self) or self.request.user.is_superuser()

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
    return True #is_manager(self) or self.request.user.is_superuser()

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
    context['students'] = Student.objects.filter(school=school)
    return context

  def test_func(self):
    return True# is_manager(self) or is_teacher(self)

class StudentDetail(UserPassesTestMixin, DetailView):
  model = Student

  def test_func(self):
    return True #is_manager(self) or is_teacher(self)

  def get_context_data(self, **kwargs):
    # xxx will be available in the template as the related objects
    context = super(StudentDetail, self).get_context_data(**kwargs)
    context['school'] = School.objects.get(pk=self.kwargs['school_id'])
    context['is_teacher'] = not self.request.user.is_anonymous()
    return context

class StudentCreate(UserPassesTestMixin, CreateView):
  model = Student
  form_class = StudentForm
  success_url = reverse_lazy('schools:school_listing')
  login_url = reverse_lazy('denied')

  def test_func(self):
    return True #is_manager(self) or self.request.user.is_superuser()

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
      form.data['user'] = User.objects.create(username=self.request.POST.get('ssn'), password=str(uuid4))

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
    return True #is_manager(self) or self.request.user.is_superuser()

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
    return True #is_manager(self) or self.request.user.is_superuser()

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
    context['studentgroups'] = StudentGroup.objects.filter(school=school)
    return context

  def test_func(self):
    return True #is_manager(self) or is_teacher(self)

class StudentGroupDetail(UserPassesTestMixin, DetailView):
  model = StudentGroup

  def test_func(self):
    return True #is_manager(self) or is_teacher(self)

  def get_context_data(self, **kwargs):
    # xxx will be available in the template as the related objects
    context = super(StudentGroupDetail, self).get_context_data(**kwargs)
    context['school'] = School.objects.get(pk=self.kwargs['school_id'])
    context['is_teacher'] = not self.request.user.is_anonymous()
    return context

class StudentGroupCreate(UserPassesTestMixin, CreateView):
  model = StudentGroup
  form_class = StudentGroupForm
  login_url = reverse_lazy('denied')

  def get_context_data(self, **kwargs):
    # xxx will be available in the template as the related objects
    context = super(StudentGroupCreate, self).get_context_data(**kwargs)
    context['school'] = School.objects.get(pk=self.kwargs['school_id'])
    return context

  def post(self, *args, **kwargs):
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
    return True #is_manager(self) or is_teacher(self)

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

  def test_func(self):
    return True #is_manager(self) or is_teacher(self)

  def get_success_url(self):
    try:
      school_id = self.kwargs['school_id']
      return reverse_lazy('schools:group_detail',
                              kwargs={'school_id': school_id, 'pk': self.kwargs['pk']})
    except:
      return reverse_lazy('schools:school_listing')

  def get_context_data(self, **kwargs):
    # xxx will be available in the template as the related objects
    context = super(StudentGroupUpdate, self).get_context_data(**kwargs)
    #context['contact_list'] = Contact.objects.filter(school=self.get_object())
    context['is_teacher'] = not self.request.user.is_anonymous()
    context['students'] = School.objects.get(pk=self.kwargs['school_id']).students
    return context

class StudentGroupDelete(UserPassesTestMixin, DeleteView):
  model = StudentGroup
  login_url = reverse_lazy('denied')
  template_name = "schools/confirm_delete.html"

  def test_func(self):
    return True #is_manager(self) or is_teacher(self)

  def get_success_url(self):
    try:
      school_id = self.kwargs['school_id']
      return reverse_lazy('schools:school_detail',
                              kwargs={'pk': school_id})
    except:
      return reverse_lazy('schools:school_listing')