from django.views.generic       import (
    ListView, CreateView, DetailView, UpdateView, DeleteView
)
from django.contrib.auth.mixins import UserPassesTestMixin

from django.core.urlresolvers import reverse_lazy

from .            import forms
from .models      import (
    Survey, SurveyType, SurveyResource,
    SurveyGradingTemplate, SurveyInputField, SurveyInputGroup
)
from .mixins      import (
    SurveySuperSuccessMixin,
    SurveyCreateSuperSuccessMixin,
    SurveyDeleteSuperSuccessMixin
)


class SurveyListing(UserPassesTestMixin, ListView):
    model = Survey

    def test_func(self):
        return self.request.user.is_authenticated()


class SurveyDetail(UserPassesTestMixin, DetailView):
    model = Survey

    def get_context_data(self, **kwargs):
        context                              = super(SurveyDetail, self).get_context_data(**kwargs)
        survey                               = Survey.objects.get(pk=self.kwargs['pk'])
        context['survey']                    = survey
        context['survey_resource_list']      = SurveyResource.objects.filter(survey=survey)
        context['survey_template_list']      = SurveyGradingTemplate.objects.filter(survey=survey)
        input_groups                         = SurveyInputGroup.objects.filter(survey=survey)
        context['survey_input_field_groups'] = input_groups
        inputs = []
        for group in input_groups:
            inputs.extend(SurveyInputField.objects.filter(
                input_group=group
            ))
        context['survey_input_field_list']   = inputs
        return context

    def test_func(self, **kwargs):
        return self.request.user.is_authenticated()


class SurveyTypeDetail(UserPassesTestMixin, DetailView):
    model = SurveyType

    def get_context_data(self, **kwargs):
        context                = super(SurveyTypeDetail, self).get_context_data(**kwargs)
        context['survey_type'] = SurveyType.objects.get(pk=self.kwargs['pk'])
        return context

    def test_func(self, **kwargs):
        return self.request.user.is_authenticated()


class SurveyTypeCreate(SurveyCreateSuperSuccessMixin, CreateView):
    model      = SurveyType
    form_class = forms.SurveyTypeForm

    def form_valid(self, form):
        survey            = form.save(commit=False)
        survey.created_by = self.request.user
        return super(SurveyTypeCreate, self).form_valid(form)

    def get_success_url(self):
        try:
            return reverse_lazy(
                'survey:survey_type_detail',
                kwargs={'pk': self.object.pk})
        except:
            return reverse_lazy('survey:survey_list')


class SurveyTypeUpdate(SurveySuperSuccessMixin, UpdateView):
    model      = SurveyType
    form_class = forms.SurveyTypeForm

    def get_success_url(self):
        try:
            return reverse_lazy(
                'survey:survey_type_detail',
                kwargs={'pk': self.kwargs['pk']})
        except:
            return reverse_lazy('survey:survey_list')


class SurveyTypeDelete(UserPassesTestMixin, DeleteView):
    model         = SurveyType
    success_url   = reverse_lazy('survey:survey_list')
    login_url     = reverse_lazy('denied')
    template_name = "survey/confirm_delete.html"

    def test_func(self):
        return self.request.user.is_superuser


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
        survey            = Survey.objects.get(pk=self.kwargs['survey_id'])
        context['survey'] = survey
        # Only get input groups related to the survey object for the select menu
        context['form'].fields['input_group'].queryset = SurveyInputGroup.objects.filter(
            survey=survey
        )
        return context


class SurveyInputFieldUpdate(SurveySuperSuccessMixin, UpdateView):
    model      = SurveyInputField
    form_class = forms.SurveyInputFieldForm

    def get_context_data(self, **kwargs):
        context           = super(SurveyInputFieldUpdate, self).get_context_data(**kwargs)
        survey            = Survey.objects.get(pk=self.kwargs['survey_id'])
        context['survey'] = survey
        # Only get input groups related to the survey object for the select menu
        context['form'].fields['input_group'].queryset = SurveyInputGroup.objects.filter(
            survey=survey
        )
        return context


class SurveyInputFieldDelete(SurveyDeleteSuperSuccessMixin, DeleteView):
    model         = SurveyInputField


class SurveyInputGroupDetail(UserPassesTestMixin, DetailView):
    model = SurveyInputGroup

    def test_func(self, **kwargs):
        return True

    def get_context_data(self, **kwargs):
        # xxx will be available in the template as the related objects
        context           = super(SurveyInputGroupDetail, self).get_context_data(**kwargs)
        context['survey'] = Survey.objects.get(pk=self.kwargs['survey_id'])
        return context


class SurveyInputGroupCreate(SurveySuperSuccessMixin, CreateView):
    model      = SurveyInputGroup
    form_class = forms.SurveyInputGroupForm

    def form_valid(self, form):
        survey            = form.save(commit=False)
        survey.created_by = self.request.user
        survey.survey     = Survey.objects.get(pk=self.kwargs['survey_id'])
        return super(SurveyInputGroupCreate, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context           = super(SurveyInputGroupCreate, self).get_context_data(**kwargs)
        context['survey'] = Survey.objects.get(pk=self.kwargs['survey_id'])
        return context


class SurveyInputGroupUpdate(SurveySuperSuccessMixin, UpdateView):
    model      = SurveyInputGroup
    form_class = forms.SurveyInputGroupForm


class SurveyInputGroupDelete(SurveyDeleteSuperSuccessMixin, DeleteView):
    model         = SurveyInputGroup
