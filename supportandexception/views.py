# -*- coding: utf-8 -*-
import csv


from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.shortcuts import render, render_to_response, get_object_or_404
from django.template import RequestContext, loader
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.auth import login
from django.views.generic import * #ListView, CreateView, DetailView, UpdateView, DeleteView
from django.core.urlresolvers import reverse

from datetime import *

from .models import *
from common.models import *

from .forms import *

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
		context['students'] = Student.objects.all()
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
		student_info = Student.objects.filter(pk=self.kwargs.get('student_id'))
		student_moreinfo = StudentExceptionSupport.objects.filter(student = student_info)
		context['student'] = student_info.get
		context['studentmorinfo'] = student_moreinfo.get
		context['supportresource'] = SupportResource.objects.filter(student = student_moreinfo).get
		context['studentgroup'] = StudentGroup.objects.filter(students = student_info).get
		context['school'] = School.objects.get(pk=self.kwargs['school_id'])
		return context

	def post(self, request, *args, **kwargs):
		print('except')
		notes = request.POST['notes']
		expl = request.POST['explanation']
		ra = request.POST.getlist('reading_assistance')
		inte = request.POST.getlist('interpretation')
		rts = request.POST.getlist('return_to_sites')
		lt = request.POST.getlist('longer_time')
		
		reading_assistance= []
		interpretation = []
		return_to_sites = []
		longer_time = []
		
		if(ra != []):
			for i in range(len(ra)):
				reading_assistance.append(int(ra[i]))
		if(inte!=[]):
			for i in range(len(inte)):
				interpretation.append(int(inte[i]))
		if(rts!=[]):
			for i in range(len(rts)):
				return_to_sites.append(int(rts[i]))
		if(lt != []):
			for i in range(len(lt)):
				longer_time.append(int(lt[i]))
		s = Student.objects.get(pk = self.kwargs.get('student_id'))
		
		
		if(SupportResource.objects.filter(student = s).exists()):
			Student.objects.filter(pk = self.kwargs.get('student_id')).update(notes = notes)
			print('fyrsti kalli')
			SupportResource.objects.filter(student = s).update(explanation = expl, signature=self.request.user, reading_assistance = reading_assistance, interpretation = interpretation, return_to_sites = return_to_sites, longer_time = longer_time)
			return HttpResponseRedirect(reverse('listi:student', args=(int(self.kwargs.get('student_id')),)))
		else:
			print('donni')
			ses = StudentExceptionSupport(notes = notes)
			ses.student = s
			print(s)
			sr = SupportResource(explanation = expl, signature=self.request.user, reading_assistance = reading_assistance, interpretation = interpretation, return_to_sites = return_to_sites, longer_time = longer_time)
			sr.student = s
			sr.save()	
			return HttpResponseRedirect(reverse('listi:student', args=(int(self.kwargs.get('student_id')),)))

		

class ExceptionCreate(CreateView):
	model = Exceptions
	form_class = ExceptionsForm
	
	def post(self, *args, **kwargs):
		self.object = None

		form = self.get_form()		
		if form.is_valid():
			return self.form_valid(form)
		else:
			return self.form_invalid(form)

	def get_context_data(self, **kwargs):
		context = super(ExceptionCreate, self).get_context_data(**kwargs)
		context['student'] = Student.objects.filter(pk=self.kwargs.get('student_id')).get

		context['exceptions'] = Exceptions.objects.filter(student = Student.objects.filter(pk=self.kwargs.get('student_id'))).get
		context['school'] = School.objects.get(pk=self.kwargs['school_id'])
		return context

	
def exception_post(request, student_id):
	if request.method == 'POST':
		expl = request.POST.get('expl')
		exam = request.POST.getlist("exam")
		notes = request.POST.get('notes')
		reason = request.POST.get('reason')
		exam =exam[0]
		
		Student.objects.filter(pk = student_id).update(notes = notes)
		if(Exceptions.objects.filter(student = Student.objects.get(pk=int(student_id))).exists()):
			Exceptions.objects.filter(student = Student.objects.get(pk=int(student_id))).update(explanation = expl, exam = exam, reason = reason,signature= str(request.user))
			return JsonResponse({"message": "Allt í lagi ok bæ"})
		else:
			exceptions = Exceptions(explanation = expl, exam = exam, reason = reason,signature= str(request.user))
			exceptions.student = Student.objects.get(pk=int(student_id))
			exceptions.save()
			return JsonResponse({"message": "Allt í lagi"})
	else:
		return JsonResponse({"message": "error"})

def exception_cancel(request, student_id):
	Exceptions.objects.filter(student = Student.objects.get(pk=int(student_id))).delete()
	return HttpResponse('kalli')

def create_post(request, student_id):
	if request.method == 'POST':
		ssn = request.POST.get('ssn')
		notes = request.POST.get('notes')		

		Student.objects.filter(pk = student_id).update(notes = notes)
 
		return JsonResponse({"message": "success"})
	else:
		return JsonResponse({"message": "error"})