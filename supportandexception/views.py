# -*- coding: utf-8 -*-
import csv


from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.shortcuts import render, render_to_response, get_object_or_404
from django.template import RequestContext, loader
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.auth import login
from django.views.generic import * #ListView, CreateView, DetailView, UpdateView, DeleteView
from django.core.urlresolvers import reverse
from django.conf import settings

from datetime import *

from .models import *
from common.models import *

from .forms import *
from rest_framework import viewsets

# Create your views here.
def Csv(request):
	title = "Nemendaskráning"
	StudentForm = StudentsForm()
	if request.method == 'POST':
		form = UploadFileForm(request.POST, request.FILES)
		if form.is_valid():
			file = request.FILES['file']
			for line in file.readlines():
				kt, nafn = line.decode('utf-8').split(';')
				Student(socialsecurity=str(kt), name=str(nafn)).save()
			#CodeCSvModel.import_data(data=open(file))

	else:
		form = UploadFileForm()

	context = {
		"title" : title,
		"StudentForm": StudentForm,
		"uploadform": form,
	}

	return render(request,"csv-import.html",context)

class ExamSupport(ListView):
	model = Student
	template_name = "supportandexception/student_list.html"
	def get_context_data(self, **kwargs):
		context = super(ExamSupport, self).get_context_data(**kwargs)
		school = School.objects.get(pk=self.kwargs['school_id'])
		
		student_info = Student.objects.filter(school=school)
		student_moreinfo = StudentExceptionSupport.objects.filter(student = student_info)
		
		context['student'] = Student.objects.filter(school=school)
		context['studentmorinfo'] = student_moreinfo
		context['studentssupport'] = SupportResource.objects.filter(student__in = student_info).all
		context['studentsexception'] = Exceptions.objects.filter(student__in = student_info).all
		context['school'] = School.objects.get(pk=self.kwargs['school_id'])
		return context



class Detail(CreateView):
	model = Student
	fields = '__all__'
	template_name = "supportandexception/student_form.html"
	def get_context_data(self, **kwargs):
		context = super(Detail, self).get_context_data(**kwargs)
		context['student'] = Student.objects.filter(pk=self.kwargs.get('student_id')).get
		context['school'] = School.objects.get(pk=self.kwargs['school_id'])
		return context


class SupportreResourceCreate(CreateView):
	model = SupportResource
	form_class = SupportResourceForm
	formset =SupportResourceFormSet

	def get_context_data(self, **kwargs):
		context = super(SupportreResourceCreate, self).get_context_data(**kwargs)
		student_info = Student.objects.filter(pk=self.kwargs.get('pk'))
		student_moreinfo = StudentExceptionSupport.objects.filter(student = student_info)
		context['student'] = student_info.get
		context['studentmorinfo'] = student_moreinfo.get
		context['supportresource'] = SupportResource.objects.filter(student = student_info).get or "''"
		context['studentgroup'] = StudentGroup.objects.filter(students = student_info).get
		context['school'] = School.objects.get(pk=self.kwargs['school_id'])

		return context

	def post(self, request, *args, **kwargs):
		if(request.POST.get('submit')== 'supportsave'):
			notes = request.POST['notes']
			expl = request.POST['explanation']
			ra = request.POST.getlist('reading_assistance')
			inte = request.POST.getlist('interpretation')
			lt = request.POST.getlist('longer_time')

			reading_assistance= []
			interpretation = []
			longer_time = []

			if(ra != []):
				for i in range(len(ra)):
					reading_assistance.append(int(ra[i]))
			if(inte!=[]):
				for i in range(len(inte)):
					interpretation.append(int(inte[i]))
			if(lt != []):
				for i in range(len(lt)):
					longer_time.append(int(lt[i]))
			s = Student.objects.get(pk = self.kwargs.get('pk'))
			if(StudentExceptionSupport.objects.filter(student = s).exists()):
				StudentExceptionSupport.objects.filter(student = s).update(notes = notes)
			else:
				ses = StudentExceptionSupport(notes = notes)
				ses.student = s
				ses.save()

			if(SupportResource.objects.filter(student = s).exists()):
				SupportResource.objects.filter(student = s).update(explanation = expl, reading_assistance = reading_assistance, interpretation = interpretation, longer_time = longer_time)
			else:
				sr = SupportResource(explanation = expl, supportresourcesignature=self.request.user, reading_assistance = reading_assistance, interpretation = interpretation, longer_time = longer_time)
				sr.student = s
				sr.save()
			return HttpResponseRedirect(reverse('schools:student_detail', args=(int(self.kwargs.get('school_id')),int(self.kwargs.get('pk')),)))
		if(request.POST.get('submit')== 'supportdelete'):
			s = Student.objects.get(pk = self.kwargs.get('pk'))
			SupportResource.objects.filter(student = s).delete()
			return HttpResponseRedirect(reverse('schools:student_detail', args=(int(self.kwargs.get('school_id')),int(self.kwargs.get('pk')),)))



class ExceptionCreate(CreateView):
	model = Exceptions
	form_class = ExceptionsForm

	def post(self, request, *args, **kwargs):
		if(request.POST.get('submit')== 'exceptionsave'):
			expl = request.POST.get('explanation')
			exam = request.POST.getlist("exam")
			notes = request.POST.get('notes')
			reason = request.POST.get('reason')
			exam_list = []
			if(exam != []):
				for i in range(len(exam)):
					exam_list.append(int(exam[i]))
			s = Student.objects.get(pk = self.kwargs.get('pk'))
			if(StudentExceptionSupport.objects.filter(student = s).exists()):
				StudentExceptionSupport.objects.filter(student = s).update(notes = notes)
			else:
				ses = StudentExceptionSupport(notes = notes)
				ses.student = s
				ses.save()
			if(Exceptions.objects.filter(student = s).exists()):
				Exceptions.objects.filter(student = s).update(explanation = expl, exam = exam_list, reason = reason)
			else:
				exceptions = Exceptions(explanation = expl, exam = exam_list, reason = reason,exceptionssignature= str(request.user))
				exceptions.student = s
				exceptions.save()
			return HttpResponseRedirect(reverse('schools:student_detail', args=(int(self.kwargs.get('school_id')),int(self.kwargs.get('pk')),)))
		if(request.POST.get('submit')== 'exceptiondelete'):
			Exceptions.objects.filter(student = Student.objects.get(pk=self.kwargs.get('pk'))).delete()
			return HttpResponseRedirect(reverse('schools:student_detail', args=(int(self.kwargs.get('school_id')),int(self.kwargs.get('pk')),)))

	def get_context_data(self, **kwargs):
		context = super(ExceptionCreate, self).get_context_data(**kwargs)
		student_info = Student.objects.filter(pk=self.kwargs.get('pk'))
		student_moreinfo = StudentExceptionSupport.objects.filter(student = student_info)
		context['student'] = student_info.get
		context['studentmorinfo'] = student_moreinfo.get
		context['studentgroup'] = StudentGroup.objects.filter(students = student_info).get
		context['exceptions'] = Exceptions.objects.filter(student = student_info).get
		context['school'] = School.objects.get(pk=self.kwargs['school_id'])
		return context

class StudentWithExceptViewSet(viewsets.ModelViewSet):
	queryset = Student.objects.all()
	serializer_class = StudentWithExceptSerializer

	def get_queryset(self):
		return Student.objects.all()
		