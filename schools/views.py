# -*- coding: utf-8 -*-
import csv

from django.http import HttpResponse
from django.shortcuts import render, render_to_response, get_object_or_404
from django.template import RequestContext, loader
from django.views.generic import ListView, CreateView, DetailView, UpdateView, DeleteView
from django.core.urlresolvers import reverse_lazy
from django.contrib.auth.mixins import UserPassesTestMixin

from .models import School, Student, StudentClass, Teacher
from .models import SchoolForm, StudentForm, StudentClassForm, TeacherForm

class SchoolListing(ListView):
  model = School

class SchoolDetail(ListView):
  model = School

  def get_context_data(self, **kwargs):
    # xxx will be available in the template as the related objects
    context = super(SchoolDetail, self).get_context_data(**kwargs)
    #context['contact_list'] = Contact.objects.filter(school=self.get_object())
    context['is_teacher'] = not self.request.user.is_anonymous()
    return context

class SchoolCreate(UserPassesTestMixin, CreateView):
  model = School
  form_class = SchoolForm
  success_url = reverse_lazy('schools:school_listing')
  login_url = reverse_lazy('denied')

  def test_func(self):
    return not self.request.user.is_anonymous()

class SchoolUpdate(UserPassesTestMixin, UpdateView):
  model = School
  form_class = SchoolForm
  login_url = reverse_lazy('denied')

  def test_func(self):
    return not self.request.user.is_anonymous()

  def get_success_url(self):
    return reverse('students:school_detail', kwargs={
      'pk': self.object.pk
    })

class SchoolDelete(UserPassesTestMixin, DeleteView):
  model = School
  success_url = reverse_lazy('schools:school_listing')
  login_url = reverse_lazy('denied')
  template_name = "schools/confirm_delete.html"

  def test_func(self):
    return not self.request.user.is_anonymous()

class StudentListing(ListView):
  model = Student

class StudentDetail(ListView):
  model = Student

  def get_context_data(self, **kwargs):
    # xxx will be available in the template as the related objects
    context = super(StudentDetail, self).get_context_data(**kwargs)
    #context['contact_list'] = Contact.objects.filter(school=self.get_object())
    context['is_teacher'] = not self.request.user.is_anonymous()
    return context

class StudentCreate(UserPassesTestMixin, CreateView):
  model = Student
  form_class = StudentForm
  success_url = reverse_lazy('schools:listing')
  login_url = reverse_lazy('denied')

  def test_func(self):
    return not self.request.user.is_anonymous()

class StudentUpdate(UserPassesTestMixin, UpdateView):
  model = Student
  form_class = StudentForm
  login_url = reverse_lazy('denied')

  def test_func(self):
    return not self.request.user.is_anonymous()

  def get_success_url(self):
    return reverse('schools:detail', kwargs={
      'pk': self.object.pk
    })

class StudentDelete(UserPassesTestMixin, DeleteView):
  model = Student
  success_url = reverse_lazy('schools:listing')
  login_url = reverse_lazy('denied')
  template_name = "schools/confirm_delete.html"

  def test_func(self):
    return not self.request.user.is_anonymous()
