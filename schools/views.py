# -*- coding: utf-8 -*-
import csv

from django.http import HttpResponse, HttpResponseRedirect
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

from common.models import School, Student, StudentGroup, Manager, Teacher, Survey, SurveyResult
from common.models import SchoolForm, StudentForm, StudentGroupForm, ManagerForm, TeacherForm, SurveyForm, SurveyResultForm

def get_current_school(path_variables):
  try:
    return path_variables['school_id']
  except:
    return path_variables['pk']

def is_school_manager(context):
  if context.request.user.is_superuser:
    return True
  try:
    school_id = get_current_school(context.kwargs)
    if School.objects.filter(pk=school_id).filter(managers=Manager.objects.filter(user=context.request.user)):
      return True
  except:
    pass
  return False

def is_school_teacher(context):
  try:
    school_id = get_current_school(context.kwargs)
    if School.objects.filter(pk=school_id).filter(teachers=Teacher.objects.filter(user=context.request.user)):
      return True
  except:
    pass
  return False

class SchoolListing(ListView):
  model = School

  def get_context_data(self, **kwargs):
    context = super(SchoolListing, self).get_context_data(**kwargs)
    try:
      if self.request.user.is_superuser:
        context['school_list'] = School.objects.all()
      else:
        manager_schools = School.objects.filter(managers=Manager.objects.filter(user=self.request.user))
        teacher_schools = School.objects.filter(teachers=Teacher.objects.filter(user=self.request.user))
        context['school_list'] = manager_schools | teacher_schools
    except Exception as e:
      print(e)
    return context

class SchoolDetail(UserPassesTestMixin, DetailView):
  model = School

  def test_func(self):
    return is_school_manager(self) or is_school_teacher(self)

  def get_context_data(self, **kwargs):
    context = super(SchoolDetail, self).get_context_data(**kwargs)
    context['studentgroup_list'] = self.object.studentgroup_set.all()
    context['managers'] = self.object.managers.all()
    context['teachers'] = self.object.teachers.all()
    context['surveys'] = Survey.objects.filter(studentgroup__in=self.object.studentgroup_set.all())
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
    return is_school_manager(self) or is_school_teacher(self)

class ManagerDetail(UserPassesTestMixin, DetailView):
  model = Manager

  def test_func(self):
    return is_school_manager(self) or is_school_teacher(self)

  def get_context_data(self, **kwargs):
    context = super(ManagerDetail, self).get_context_data(**kwargs)
    context['is_teacher'] = not self.request.user.is_anonymous()
    context['school'] = School.objects.get(pk=self.kwargs['school_id'])
    return context

class ManagerCreate(UserPassesTestMixin, CreateView):
  model = Manager
  form_class = ManagerForm
  login_url = reverse_lazy('denied')

  def test_func(self):
    return is_school_manager(self)

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
    return is_school_manager(self)

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
    return is_school_manager(self)

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
    return is_school_manager(self) or is_school_teacher(self)

class TeacherDetail(UserPassesTestMixin, DetailView):
  model = Teacher

  def test_func(self):
    return is_school_manager(self) or is_school_teacher(self)

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
    return is_school_manager(self)

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
    return is_school_manager(self)

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
    return is_school_manager(self)

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
    return is_school_manager(self) or is_school_teacher(self)

class StudentDetail(UserPassesTestMixin, DetailView):
  model = Student

  def test_func(self):
    return is_school_manager(self) or is_school_teacher(self)

  def get_context_data(self, **kwargs):
    # xxx will be available in the template as the related objects
    context = super(StudentDetail, self).get_context_data(**kwargs)
    context['school'] = School.objects.get(pk=self.kwargs['school_id'])
    context['is_teacher'] = not self.request.user.is_anonymous()
    return context

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
      ssn = self.request.POST.get('student_ssn')
      name = self.request.POST.get('student_name')
      if len(name) == 0 or len(ssn) == 0:
        return HttpResponse("Það verður að velja dálkanúmer")
      else:
        data = []
        for row in self.request.FILES['file'].readlines():
          row = row.decode('utf-8')
          student_ssn = row.split(',')[int(ssn)]
          student_name = row.split(',')[int(name)]
          data.append({'name': student_name.strip(), 'ssn': student_ssn.strip()})
      return render(self.request, 'common/student_verify_import.html', {'data': data, 'school': School.objects.get(pk=self.kwargs['school_id'])})
    else:
      student_data = json.loads(self.request.POST['students'])
      school = School.objects.get(pk=self.kwargs['school_id'])
      #iterate through students, add them if they don't exist then add to school
      for student in student_data:
        try:
          s = Student.objects.create(**student)
        except:
          pass #student already exists
        school.students.add(s)

    return HttpResponseRedirect(self.get_success_url())

  def test_func(self):
    return is_school_manager(self)

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
    return is_school_manager(self)

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
    return is_school_manager(self)

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
    return is_school_manager(self)

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
    return is_school_manager(self) or is_school_teacher(self)

class StudentGroupDetail(UserPassesTestMixin, DetailView):
  model = StudentGroup

  def test_func(self):
    return is_school_manager(self) or is_school_teacher(self)

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
    return is_school_manager(self) or is_school_teacher(self)

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
    return is_school_manager(self) or is_school_teacher(self) #TODO: manager or (teacher and group_manager)

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
    return is_school_manager(self) or is_school_teacher(self) #TODO: manager or (teacher and group_manager)

  def get_success_url(self):
    try:
      school_id = self.kwargs['school_id']
      return reverse_lazy('schools:school_detail',
                              kwargs={'pk': school_id})
    except:
      return reverse_lazy('schools:school_listing')

class SurveyListing(UserPassesTestMixin, ListView):
  model = Survey

  def test_func(self):
    return is_school_manager(self) or is_school_teacher(self)

class SurveyDetail(UserPassesTestMixin, DetailView):
  model = Survey

  def test_func(self):
    return is_school_manager(self) or is_school_teacher(self)

  def get_context_data(self, **kwargs):
    # xxx will be available in the template as the related objects
    context = super(SurveyDetail, self).get_context_data(**kwargs)
    context['school'] = School.objects.get(pk=self.kwargs['school_id'])
    context['students'] = self.object.studentgroup.students.all()
    context['is_teacher'] = not self.request.user.is_anonymous()
    return context

class SurveyCreate(UserPassesTestMixin, CreateView):
  model = Survey
  form_class = SurveyForm
  login_url = reverse_lazy('denied')

  def get_survey(self):
    try:
        r = requests.get(settings.PROFAGRUNNUR_URL)
        return r.json()
    except:
      return []

  def get_form(self):
    form = super(SurveyCreate, self).get_form(self.form_class)
    form.fields['studentgroup'].queryset = StudentGroup.objects.filter(school=self.kwargs['school_id'])
    return form

  def get_context_data(self, **kwargs):
      # xxx will be available in the template as the related objects
      context = super(SurveyCreate, self).get_context_data(**kwargs)
      context['survey_list'] = self.get_survey()
      return context

  def test_func(self):
    return is_school_manager(self) or is_school_teacher(self) #TODO: manager or (teacher and group_manager)

  def get_success_url(self):
    try:
      school_id = self.kwargs['school_id']
      return reverse_lazy('schools:school_detail',
                              kwargs={'pk': school_id})
    except:
      return reverse_lazy('schools:school_listing')

class SurveyUpdate(UserPassesTestMixin, UpdateView):
  model = Survey
  form_class = SurveyForm
  login_url = reverse_lazy('denied')

  def test_func(self):
    return is_school_manager(self) or is_school_teacher(self) #TODO: manager or (teacher and group_manager)

  def get_survey(self):
    try:
        r = requests.get(settings.PROFAGRUNNUR_URL)
        return r.json()
    except:
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
    return is_school_manager(self) or is_school_teacher(self) #TODO: manager or (teacher and group_manager)

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

class SurveyResultCreate(UserPassesTestMixin, CreateView):
  model = SurveyResult
  form_class = SurveyResultForm
  login_url = reverse_lazy('denied')

  def get_context_data(self, **kwargs):
    # xxx will be available in the template as the related objects
    context = super(SurveyResultCreate, self).get_context_data(**kwargs)
    context['data_fields'] = json.loads(Survey.objects.get(pk=self.kwargs['survey_id']).data_fields)
    context['data_result'] = {'error': 'no value'}
    context['student'] = Student.objects.filter(pk=self.kwargs['student_id'])
    context['survey'] = Survey.objects.filter(pk=self.kwargs['survey_id'])
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
    survey_results.reported_by =Teacher.objects.get(pk=self.request.user.pk)
    survey_results.student = Student.objects.get(pk=self.kwargs['student_id'])
    survey_results.survey = Survey.objects.get(pk=self.kwargs['survey_id'])
    survey_results.created_at = timezone.now()
    data_fields = json.loads(Survey.objects.get(pk=self.kwargs['survey_id']).data_fields)
    data_results = {}
    for field in data_fields:
      data_results[field['field_name']] = self.request.POST[field['field_name']]
    survey_results.results = json.dumps(data_results)
    #save()  # This is redundant, see comments.
    return super(SurveyResultCreate, self).form_valid(form)

  def test_func(self):
    return is_school_manager(self) or is_school_teacher(self) #TODO: manager or (teacher and group_manager)

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
    return is_school_manager(self) or is_school_teacher(self) #TODO: manager or (teacher and group_manager)

  def form_valid(self, form):
    survey_results = form.save(commit=False)
    survey_results.created_at = timezone.now()
    data_fields = json.loads(Survey.objects.get(pk=self.kwargs['survey_id']).data_fields)
    data_results = {}
    for field in data_fields:
      data_results[field['field_name']] = self.request.POST[field['field_name']]
    survey_results.results = json.dumps(data_results)
    #save()  # This is redundant, see comments.
    return super(SurveyResultUpdate, self).form_valid(form)

  def get_context_data(self, **kwargs):
    # xxx will be available in the template as the related objects
    context = super(SurveyResultUpdate, self).get_context_data(**kwargs)
    context['data_fields'] = json.loads(Survey.objects.get(pk=self.kwargs['survey_id']).data_fields)
    context['student'] = Student.objects.filter(pk=self.kwargs['student_id'])
    context['survey'] = Survey.objects.filter(pk=self.kwargs['survey_id'])
    context['data_result'] = json.loads(SurveyResult.objects.get(pk=self.kwargs['pk']).results)
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
    return is_school_manager(self) or is_school_teacher(self) #TODO: manager or (teacher and group_manager)

  def get_success_url(self):
    try:
      school_id = self.kwargs['school_id']
      return reverse_lazy('schools:school_detail',
                              kwargs={'pk': school_id})
    except:
      return reverse_lazy('schools:school_listing')