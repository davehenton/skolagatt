
# -*- coding: utf-8 -*-
from django.http                import HttpResponseRedirect
from django.shortcuts           import render
from django.views.generic       import ListView, CreateView
from django.core.urlresolvers   import reverse
from django.contrib.auth.models import User

from rest_framework import viewsets

from .             import models
from common.models import Student, StudentGroup, School, Manager, GroupSurvey
from common.forms  import StudentForm
from .             import forms
from common.util   import is_school_manager


def Csv(request):
    title       = "Nemendaskráning"
    if request.method == 'POST':
        form = forms.UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES['file']
            for line in file.readlines():
                kt, nafn = line.decode('utf-8').split(';')
                Student(socialsecurity=str(kt), name=str(nafn)).save()

    else:
        form = forms.UploadFileForm()

    context = {
        "title"      : title,
        "StudentForm": StudentForm(),
        "uploadform" : form,
    }

    return render(request, "csv-import.html", context)


class ExamSupport(ListView):
    model         = Student
    template_name = "supportandexception/student_list.html"

    def get_context_data(self, **kwargs):
        context = super(ExamSupport, self).get_context_data(**kwargs)
        school  = School.objects.get(pk=self.kwargs['school_id'])

        student_info     = Student.objects.filter(school=school)
        groupsurvey      = GroupSurvey.objects.get(pk=self.kwargs.get('groupsurvey_id'))
        student_moreinfo = models.StudentExceptionSupport.objects.filter(student = student_info, groupsurvey = groupsurvey)

        context['student']           = Student.objects.filter(school=school)
        context['studentmorinfo']    = student_moreinfo
        context['studentssupport']   = models.SupportResource.objects.filter(
            student__in = student_info, groupsurvey = groupsurvey).all
        context['studentsexception'] = models.Exceptions.objects.filter(
            student__in = student_info, groupsurvey = groupsurvey).all
        context['school']            = School.objects.get(pk=self.kwargs['school_id'])
        context['groupsurvey']       = groupsurvey
        return context


class Detail(CreateView):
    model         = Student
    fields        = '__all__'
    template_name = "supportandexception/student_form.html"

    def get_context_data(self, **kwargs):
        context                = super(Detail, self).get_context_data(**kwargs)
        context['student']     = Student.objects.filter(pk=self.kwargs.get('student_id')).get
        context['school']      = School.objects.get(pk=self.kwargs['school_id'])
        context['groupsurvey'] = GroupSurvey.objects.get(pk=self.kwargs['groupsurvey_id'])
        return context


class SupportResourceCreate(CreateView):
    model      = models.SupportResource
    form_class = forms.SupportResourceForm
    formset    = forms.SupportResourceFormSet

    def get_context_data(self, **kwargs):
        context          = super(SupportResourceCreate, self).get_context_data(**kwargs)
        student_info     = Student.objects.filter(pk=self.kwargs.get('pk'))
        groupsurvey      = GroupSurvey.objects.get(pk=self.kwargs.get('groupsurvey_id'))
        student_moreinfo = models.StudentExceptionSupport.objects.filter(student = student_info, groupsurvey=groupsurvey)

        context['student']         = student_info.get
        context['studentmorinfo']  = student_moreinfo.get
        context['supportresource'] = models.SupportResource.objects.filter(
            student = student_info).get or "''"
        context['studentgroup']    = StudentGroup.objects.filter(students = student_info).get
        context['school']          = School.objects.get(pk=self.kwargs['school_id'])
        context['groupsurvey']     = groupsurvey

        return context

    def post(self, request, *args, **kwargs):
        groupsurvey  = GroupSurvey.objects.get(pk=self.kwargs.get('groupsurvey_id'))
        response_url = reverse(
            'schools:survey_detail',
            args=(int(self.kwargs.get('school_id')), int(groupsurvey.studentgroup.id), int(groupsurvey.id))
        )
        if (request.POST.get('submit') == 'supportsave'):
            ra    = request.POST.getlist('reading_assistance')
            inte  = request.POST.getlist('interpretation')
            lt    = request.POST.getlist('longer_time')

            reading_assistance = []
            interpretation     = []
            longer_time        = []

            if (ra != []):
                for i in range(len(ra)):
                    reading_assistance.append(int(ra[i]))
            if (inte != []):
                for i in range(len(inte)):
                    interpretation.append(int(inte[i]))
            if (lt != []):
                for i in range(len(lt)):
                    longer_time.append(int(lt[i]))
            s = Student.objects.get(pk = self.kwargs.get('pk'))
            gs = GroupSurvey.objects.get(pk = self.kwargs.get('groupsurvey_id'))
            if not (models.StudentExceptionSupport.objects.filter(student = s, groupsurvey = gs).exists()):
                ses         = models.StudentExceptionSupport()
                ses.student = s
                ses.groupsurvey = gs
                ses.save()

            if (models.SupportResource.objects.filter(student = s, groupsurvey = gs).exists()):
                models.SupportResource.objects.filter(student = s, groupsurvey = gs).update(
                    reading_assistance = reading_assistance,
                    interpretation     = interpretation,
                    longer_time        = longer_time
                )
            else:
                sr = models.SupportResource(
                    supportresourcesignature = Manager.objects.get(
                        user=User.objects.filter(username=self.request.user)),
                    reading_assistance       = reading_assistance,
                    interpretation           = interpretation,
                    longer_time              = longer_time
                )
                sr.student = s
                sr.groupsurvey = gs
                sr.save()
            return HttpResponseRedirect(response_url)
        if (request.POST.get('submit') == 'supportdelete'):
            s = Student.objects.get(pk = self.kwargs.get('pk'))
            gs = GroupSurvey.objects.get(pk = self.kwargs.get('groupsurvey_id'))
            models.SupportResource.objects.filter(student = s, groupsurvey = gs).delete()
            return HttpResponseRedirect(response_url)
        if (request.POST.get('submit') == 'supportgothrough'):
            return HttpResponseRedirect(response_url)


class ExceptionCreate(CreateView):
    model      = models.Exceptions
    form_class = forms.ExceptionsForm

    def test_func(self):
        return is_school_manager(self.request, self.kwargs)

    def post(self, request, *args, **kwargs):
        groupsurvey  = GroupSurvey.objects.get(pk=self.kwargs.get('groupsurvey_id'))
        response_url = reverse(
            'schools:survey_detail',
            args=(int(self.kwargs.get('school_id')), int(groupsurvey.studentgroup.id), int(groupsurvey.id))
        )
        if (request.POST.get('submit') == 'exceptionsave'):
            exam      = request.POST.getlist("exam")
            reason    = request.POST.get('reason')
            exam_list = []
            if (exam != []):
                for i in range(len(exam)):
                    exam_list.append(int(exam[i]))
            s = Student.objects.get(pk = self.kwargs.get('pk'))
            gs = GroupSurvey.objects.get(pk = self.kwargs.get('groupsurvey_id'))
            if not (models.StudentExceptionSupport.objects.filter(student = s, groupsurvey = gs).exists()):
                ses         = models.StudentExceptionSupport()
                ses.student = s
                ses.groupsurvey = gs
                ses.save()
            if (models.Exceptions.objects.filter(student = s, groupsurvey = gs).exists()):
                models.Exceptions.objects.filter(student = s, groupsurvey = gs).update(
                    exam = exam_list,
                )
            else:
                exceptions = models.Exceptions(
                    exam = exam_list,
                    exceptionssignature = Manager.objects.get(
                        user=User.objects.filter(username=self.request.user)
                    )
                )
                exceptions.student = s
                exceptions.groupsurvey = gs
                exceptions.save()
            return HttpResponseRedirect(response_url)
        if (request.POST.get('submit') == 'exceptiondelete'):
            models.Exceptions.objects.filter(
                student = Student.objects.get(pk=self.kwargs.get('pk')),
                groupsurvey = GroupSurvey.objects.get(pk=self.kwargs.get('groupsurvey_id')),
            ).delete()
            return HttpResponseRedirect(response_url)
        if (request.POST.get('submit') == 'exceptiongothrough'):
            return HttpResponseRedirect(response_url)

    def get_context_data(self, **kwargs):
        context          = super(ExceptionCreate, self).get_context_data(**kwargs)
        student_info     = Student.objects.filter(pk=self.kwargs.get('pk'))
        groupsurvey      = GroupSurvey.objects.get(pk=self.kwargs['groupsurvey_id'])
        student_moreinfo = models.StudentExceptionSupport.objects.filter(student = student_info, groupsurvey = groupsurvey)
        exceptions       = models.Exceptions.objects.filter(student = student_info, groupsurvey = groupsurvey)

        context['student']        = student_info.get
        context['studentmorinfo'] = student_moreinfo.get
        context['studentgroup']   = StudentGroup.objects.filter(students = student_info).get
        context['exceptions']     = exceptions.get
        context['school']         = School.objects.get(pk=self.kwargs['school_id'])
        context['groupsurvey']    = groupsurvey
        return context


class StudentWithExceptViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = models.StudentWithExceptSerializer

    def get_queryset(self):
        return Student.objects.all()
