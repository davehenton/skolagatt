from django.views.generic       import (
    ListView, CreateView, DetailView, UpdateView, DeleteView
)
from django.contrib.auth.mixins import UserPassesTestMixin

from django.core.urlresolvers import reverse_lazy

from rest_framework import viewsets

from .            import forms
from .serializers import SurveySerializer
from .models      import (
    Survey, SurveyText, SurveyResource,
    SurveyGradingTemplate, SurveyInputField
)
from .mixins      import (
    SurveySuperSuccessMixin,
    SurveyCreateSuperSuccessMixin,
    SurveyDeleteSuperSuccessMixin
)

from datetime  import datetime

from django.conf import settings


class SurveyListing(UserPassesTestMixin, ListView):
    model = Survey

    def test_func(self):
        return self.request.user.is_authenticated()


class SurveyDetail(UserPassesTestMixin, DetailView):
    model = Survey

    def get_context_data(self, **kwargs):
        context                            = super(SurveyDetail, self).get_context_data(**kwargs)
        survey                             = Survey.objects.get(pk=self.kwargs['pk'])
        context['survey']                  = survey
        context['survey_text_list']        = SurveyText.objects.filter(survey=survey)
        context['survey_resource_list']    = SurveyResource.objects.filter(survey=survey)
        context['survey_template_list']    = SurveyGradingTemplate.objects.filter(survey=survey)
        context['survey_input_field_list'] = SurveyInputField.objects.filter(survey=survey)
        return context

    def test_func(self, **kwargs):
        return self.request.user.is_authenticated()


class SurveyViewSet(viewsets.ModelViewSet):
    queryset = Survey.objects.all()
    serializer_class = SurveySerializer

    def get_queryset(self):
        try:
            if settings.JSON_API_KEY in self.request.GET.get('json_api_key'):
                return Survey.objects.filter(
                    active_to__gte   = datetime.now(),
                    active_from__lte = datetime.now()
                )
        except Exception as e:
            print(e)
            pass
        return Survey.objects.none()


class SurveyViewSetDetail(viewsets.ModelViewSet):
    queryset         = Survey.objects.all()
    serializer_class = SurveySerializer

    def get_queryset(self):
        try:
            if settings.JSON_API_KEY in self.request.GET.get('json_api_key'):
                return Survey.objects.filter(pk=self.kwargs['survey_id'])
        except:
            pass
        return Survey.objects.none()


class SurveyCreate(SurveyCreateSuperSuccessMixin, CreateView):
    model      = Survey
    form_class = forms.SurveyForm

    def form_valid(self, form):
        survey            = form.save(commit=False)
        survey.created_by = self.request.user
        return super(SurveyCreate, self).form_valid(form)


class SurveyUpdate(SurveySuperSuccessMixin, UpdateView):
    model      = Survey
    form_class = forms.SurveyForm


class SurveyDelete(UserPassesTestMixin, DeleteView):
    model         = Survey
    success_url   = reverse_lazy('survey:survey_list')
    login_url     = reverse_lazy('denied')
    template_name = "survey/confirm_delete.html"

    def test_func(self):
        return self.request.user.is_superuser


class SurveyTextDetail(UserPassesTestMixin, DetailView):
    model = SurveyText

    def test_func(self, **kwargs):
        return True

    def get_context_data(self, **kwargs):
        # xxx will be available in the template as the related objects
        context           = super(SurveyTextDetail, self).get_context_data(**kwargs)
        context['survey'] = Survey.objects.get(pk=self.kwargs['survey_id'])
        return context


class SurveyTextCreate(SurveySuperSuccessMixin, CreateView):
    model      = SurveyText
    form_class = forms.SurveyTextForm

    def form_valid(self, form):
        survey            = form.save(commit=False)
        survey.created_by = self.request.user
        survey.survey     = Survey.objects.get(pk=self.kwargs['survey_id'])
        return super(SurveyTextCreate, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context           = super(SurveyTextCreate, self).get_context_data(**kwargs)
        context['survey'] = Survey.objects.get(pk=self.kwargs['survey_id'])
        return context


class SurveyTextUpdate(SurveySuperSuccessMixin, UpdateView):
    model      = SurveyText
    form_class = forms.SurveyTextForm


class SurveyTextDelete(SurveyDeleteSuperSuccessMixin, DeleteView):
    model         = SurveyText


class SurveyResourceDetail(UserPassesTestMixin, DetailView):
    model = SurveyResource

    def test_func(self, **kwargs):
        return True

    def get_context_data(self, **kwargs):
        # xxx will be available in the template as the related objects
        context           = super(SurveyResourceDetail, self).get_context_data(**kwargs)
        context['survey'] = Survey.objects.get(pk=self.kwargs['survey_id'])
        return context


class SurveyResourceCreate(SurveySuperSuccessMixin, CreateView):
    model      = SurveyResource
    form_class = forms.SurveyResourceForm

    def form_valid(self, form):
        survey            = form.save(commit=False)
        survey.created_by = self.request.user
        survey.survey     = Survey.objects.get(pk=self.kwargs['survey_id'])
        return super(SurveyResourceCreate, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context           = super(SurveyResourceCreate, self).get_context_data(**kwargs)
        context['survey'] = Survey.objects.get(pk=self.kwargs['survey_id'])
        return context


class SurveyResourceUpdate(SurveySuperSuccessMixin, UpdateView):
    model      = SurveyResource
    form_class = forms.SurveyResourceForm


class SurveyResourceDelete(SurveyDeleteSuperSuccessMixin, DeleteView):
    model         = SurveyResource


class SurveyGradingTemplateDetail(UserPassesTestMixin, DetailView):
    model = SurveyGradingTemplate

    def test_func(self, **kwargs):
        return True

    def get_context_data(self, **kwargs):
        # xxx will be available in the template as the related objects
        context           = super(SurveyGradingTemplateDetail, self).get_context_data(**kwargs)
        context['survey'] = Survey.objects.get(pk=self.kwargs['survey_id'])
        return context


class SurveyGradingTemplateCreate(SurveySuperSuccessMixin, CreateView):
    model      = SurveyGradingTemplate
    form_class = forms.SurveyGradingTemplateForm

    def form_valid(self, form):
        survey            = form.save(commit=False)
        survey.created_by = self.request.user
        survey.survey     = Survey.objects.get(pk=self.kwargs['survey_id'])
        return super(SurveyGradingTemplateCreate, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context           = super(SurveyGradingTemplateCreate, self).get_context_data(**kwargs)
        context['survey'] = Survey.objects.get(pk=self.kwargs['survey_id'])
        return context


class SurveyGradingTemplateUpdate(SurveySuperSuccessMixin, UpdateView):
    model      = SurveyGradingTemplate
    form_class = forms.SurveyGradingTemplateForm


class SurveyGradingTemplateDelete(SurveyDeleteSuperSuccessMixin, DeleteView):
    model         = SurveyGradingTemplate


class SurveyInputFieldDetail(UserPassesTestMixin, DetailView):
    model = SurveyInputField

    def test_func(self, **kwargs):
        return True

    def get_context_data(self, **kwargs):
        # xxx will be available in the template as the related objects
        context           = super(SurveyInputFieldDetail, self).get_context_data(**kwargs)
        context['survey'] = Survey.objects.get(pk=self.kwargs['survey_id'])
        return context


class SurveyInputFieldCreate(SurveySuperSuccessMixin, CreateView):
    model      = SurveyInputField
    form_class = forms.SurveyInputFieldForm

    def form_valid(self, form):
        survey            = form.save(commit=False)
        survey.created_by = self.request.user
        survey.survey     = Survey.objects.get(pk=self.kwargs['survey_id'])
        return super(SurveyInputFieldCreate, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context           = super(SurveyInputFieldCreate, self).get_context_data(**kwargs)
        context['survey'] = Survey.objects.get(pk=self.kwargs['survey_id'])
        return context


class SurveyInputFieldUpdate(SurveySuperSuccessMixin, UpdateView):
    model      = SurveyInputField
    form_class = forms.SurveyInputFieldForm


class SurveyInputFieldDelete(SurveyDeleteSuperSuccessMixin, DeleteView):
    model         = SurveyInputField
