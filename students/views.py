# -*- coding: utf-8 -*-
import csv


from django.http import HttpResponse
from django.shortcuts import render, render_to_response, get_object_or_404
from django.template import RequestContext, loader
from django.views.generic import ListView, CreateView, DetailView, UpdateView, DeleteView
from django.core.urlresolvers import reverse_lazy
from django.contrib.auth.mixins import UserPassesTestMixin

from .models import Student, StudentClass, Teacher
from .models import StudentForm, StudentClassForm, TeacherForm

class StudentListing(ListView):
	model = Student

class StudentDetail(ListView):
	model = Student

	def get_context_data(self, **kwargs):
		# xxx will be available in the template as the related objects
		context = super(OpportunityDetail, self).get_context_data(**kwargs)
		#context['contact_list'] = Contact.objects.filter(school=self.get_object())
		context['is_teacher'] = not self.request.user.is_anonymous()
		return context

class StudentCreate(UserPassesTestMixin, CreateView):
	model = Student
	form_class = StudentForm
	success_url = reverse_lazy('students:listing')
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
		return reverse('students:detail', kwargs={
			'pk': self.object.pk
		})

class StudentDelete(UserPassesTestMixin, DeleteView):
	model = Student
	success_url = reverse_lazy('students:listing')
	login_url = reverse_lazy('denied')
	template_name = "students/confirm_delete.html"

	def test_func(self):
		return not self.request.user.is_anonymous()