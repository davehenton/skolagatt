# -*- coding: utf-8 -*-
from django.contrib.auth.mixins import UserPassesTestMixin
from django.core.urlresolvers import reverse_lazy


class SurveySuperSuccessMixin(UserPassesTestMixin):
    login_url = reverse_lazy('denied')

    def test_func(self):
        return self.request.user.is_superuser

    def get_success_url(self):
        try:
            return reverse_lazy(
                'survey:survey_detail',
                kwargs={'pk': self.kwargs['survey_id']})
        except:
            return reverse_lazy('survey:survey_list')


class SurveyCreateSuperSuccessMixin(SurveySuperSuccessMixin):

    def get_success_url(self):
        try:
            return reverse_lazy(
                'survey:survey_detail',
                kwargs={'pk': self.kwargs['survey_id']})
        except:
            return reverse_lazy('survey:survey_list')


class SurveyDeleteSuperSuccessMixin(SurveyCreateSuperSuccessMixin):
    template_name = "survey/confirm_delete.html"
