from django.http                  import HttpResponse
from django.shortcuts           import render, redirect
from django.views.generic       import (
    ListView, CreateView, DetailView, UpdateView, DeleteView
)
from django.contrib.auth.mixins import UserPassesTestMixin

from django.core.urlresolvers import reverse_lazy
import openpyxl
from openpyxl.chart import AreaChart, Reference, Series
from openpyxl.styles import Color, PatternFill

from ast       import literal_eval

from .            import forms
from .models      import (
    Survey, SurveyType, SurveyResource, SurveyTransformation,
    SurveyGradingTemplate, SurveyInputField, SurveyInputGroup
)
import common.util   as common_util
from common.models      import (
    School, SurveyResult, StudentGroup, GroupSurvey
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
        context['survey_transformation_list'] = SurveyTransformation.objects.filter(survey=survey)
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
        return reverse_lazy('survey:survey_list')


class SurveyTypeUpdate(SurveySuperSuccessMixin, UpdateView):
    model      = SurveyType
    form_class = forms.SurveyTypeForm

    def get_success_url(self):
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
    form_class = forms.SurveyInputGroupCreateForm

    def form_valid(self, form):
        input_group        = form.save(commit=False)
        input_group.survey = Survey.objects.get(pk=self.kwargs['survey_id'])
        input_group.save()  # Save input group now so we can link inputfields to it
        # Create related SurveyInputFields
        nr_inputs   = int(self.request.POST['inputs'])
        for x in range(0, nr_inputs):
            inputfield = SurveyInputField(
                name=x + 1, label=input_group.title, input_group=input_group
            )
            inputfield.save()

        return super(SurveyInputGroupCreate, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context           = super(SurveyInputGroupCreate, self).get_context_data(**kwargs)
        context['survey'] = Survey.objects.get(pk=self.kwargs['survey_id'])
        return context


class SurveyInputGroupUpdate(SurveySuperSuccessMixin, UpdateView):
    model      = SurveyInputGroup
    form_class = forms.SurveyInputGroupForm

    def form_valid(self, form):
        input_group        = form.save(commit=False)
        input_group.survey = Survey.objects.get(pk=self.kwargs['survey_id'])
        input_group.save()  # Save input group now so we can link inputfields to it
        # Create related SurveyInputFields
        nr_inputs   = int(self.request.POST['inputs'])
        nr_inputs_saved = input_group.num_input_fields()
        if nr_inputs_saved > nr_inputs:
            for x in range(nr_inputs, nr_inputs_saved):
                SurveyInputField.objects.get(input_group=input_group, name=x + 1).delete()
        elif nr_inputs_saved < nr_inputs:
            for x in range(0, nr_inputs):
                inputfield = SurveyInputField.objects.get_or_create(
                    name=x + 1, label=input_group.title, input_group=input_group
                )

        return super(SurveyInputGroupUpdate, self).form_valid(form)


class SurveyInputGroupDelete(SurveyDeleteSuperSuccessMixin, DeleteView):
    model = SurveyInputGroup


# Transformation


class SurveyTransformationDetail(UserPassesTestMixin, DetailView):
    model         = SurveyTransformation

    def get_context_data(self, **kwargs):
        # xxx will be available in the template as the related objects
        context           = super(SurveyTransformationDetail, self).get_context_data(**kwargs)
        context['survey'] = Survey.objects.get(pk=self.kwargs['survey_id'])
        transformation = SurveyTransformation.objects.get(pk=self.kwargs['pk'])
        context['transformation'] = transformation
        return context

    def test_func(self, **kwargs):
        return self.request.user.is_authenticated()


class SurveyTransformationCreate(SurveySuperSuccessMixin, CreateView):
    model      = SurveyTransformation
    form_class = forms.SurveyTransformationForm

    def get_context_data(self, **kwargs):
        context           = super(SurveyTransformationCreate, self).get_context_data(**kwargs)
        context['survey'] = Survey.objects.get(pk=self.kwargs['survey_id'])
        return context

    def post(self, *args, **kwargs):
        if(self.request.FILES):
            try:
                input_excel = self.request.FILES['file']
                book        = openpyxl.load_workbook(filename = input_excel)
                name        = self.request.POST.get('transformationname')
                unit        = self.request.POST.get('transformationunit')
                survey      = self.kwargs['survey_id']
                result_data = {}
                for sheet in book.worksheets:
                    # import pdb; pdb.set_trace()
                    for index, row in enumerate(
                            sheet.iter_rows('A{}:B{}'.format(sheet.min_row + 1, sheet.max_row))):
                        # result_data[row] = float(sheet.cell(row, 1))
                        result_data[int(sheet.cell(row=index + 2 , column=1).value)] = float(
                            sheet.cell(row=index + 2 , column=2).value)
                # order select
                transform = SurveyTransformation(name = name, order = 1, data = result_data, unit= unit)
                transform.survey = Survey.objects.get(id=survey)
                transform.save()

            except Exception as e:
                return render(
                    self.request,
                    'survey/surveytransformation_form.html',
                    {'pk': self.kwargs['survey_id']},
                    {'error': 'Dálkur ekki til, reyndu aftur'}
                )
        return redirect(self.get_success_url())   

    def get_success_url(self):
        if 'school_id' in self.kwargs:
            return reverse_lazy(
                'samraemd:math_listing',
                kwargs={'pk': self.kwargs['survey_id']}
            )
        return reverse_lazy('survey:survey_detail',
                kwargs={'pk': self.kwargs['survey_id']})


class SurveyTransformationDelete(SurveyDeleteSuperSuccessMixin, DeleteView):
    model         = SurveyTransformation


class AdminOutput(UserPassesTestMixin, ListView):
    model      = Survey
    template_name = "survey/survey_admin_filter.html"

    def get_context_data(self, **kwargs):
        # xxx will be available in the template as the related objects
        context           = super(AdminOutput, self).get_context_data(**kwargs)
        context['schools'] = School.objects.all()
        context['surveytypes'] = SurveyType.objects.all()
        context['surveys'] = Survey.objects.all()
        return context

    def test_func(self):
        return self.request.user.is_superuser

def _generate_excel_audun():
#def admin_output_excel(request):
#    print('hello')
        
    
#    response = HttpResponse(
#        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
#    response['Content-Disposition'] = 'attachment; filename=Þjálguðgögn.xlsx'

    wb       = openpyxl.Workbook()
    
    
    for year in range(1,11):
        index = 2
        title = "Árgangur {}".format(year)
        ws = wb.create_sheet(title=title)
        ws['A1'] = 'Kennitala nemanda'
        ws['B1'] = 'Nafn'
        ws['C1'] = 'September'
        ws['D1'] = 'Janúar'
        ws['E1'] = 'Mismunur'
        ws['F1'] = 'September óþjálgað'
        ws['G1'] = 'Janúar óþjálgað'

        sept_identifier = "{}b_LF_sept".format(year)
        surveys = Survey.objects.filter(survey_type_id = 2,student_year = year, identifier = sept_identifier)
        groups = StudentGroup.objects.filter(student_year = year).all()
        for survey in surveys:
            survey_type = SurveyType.objects.filter(survey=survey.id).values('id')
            dic = survey_type[0]
            survey_type = dic['id']
            transformation_sept = SurveyTransformation.objects.filter(survey=survey)
            for group in groups:
                groupsurveys = GroupSurvey.objects.filter(studentgroup = group, survey = survey).all()
                for groupsurvey in groupsurveys:
                    results = SurveyResult.objects.filter(survey = groupsurvey)
                    for result_sept in results:
                        ws.cell('A' + str(index)).value = result_sept.student.ssn
                        ws.cell('B' + str(index)).value = result_sept.student.name
                        try:
                            r_sept = literal_eval(result_sept.results)
                            survey_student_result_sept = common_util.calc_survey_results(
                                sept_identifier,
                                literal_eval(r_sept['click_values']),
                                r_sept['input_values'],
                                result_sept.student,
                                survey_type,
                                transformation_sept,
                            )
                            survey_student_result_sept_nt = common_util.calc_survey_results(
                                sept_identifier,
                                literal_eval(r_sept['click_values']),
                                r_sept['input_values'],
                                result_sept.student,
                                survey_type,
                            )
                           
                            if not survey_student_result_sept[0] == '':
                                ws.cell('C' + str(index)).value = survey_student_result_sept[0]
                            if not survey_student_result_sept_nt[0] == '':
                                ws.cell('F' + str(index)).value = survey_student_result_sept_nt[0]
                        except Exception as e:
                            print('sept' + str(e))

                        jan_identifier = "b{}_LF_jan17".format(year)
                        jan_survey = Survey.objects.filter(identifier = jan_identifier).first()
                        transformation_jan = SurveyTransformation.objects.filter(survey=jan_survey)
                        jan_gs = GroupSurvey.objects.filter(survey = jan_survey, studentgroup = groupsurvey.studentgroup).first()
                        #import pdb; pdb.set_trace()
                        
                        if SurveyResult.objects.filter(student = result_sept.student, survey = jan_gs).exists():
                            result_jan = SurveyResult.objects.filter(student = result_sept.student, survey = jan_gs).first()
                            try:
                                r_jan = literal_eval(result_jan.results)
                                survey_student_result_jan = common_util.calc_survey_results(
                                    jan_identifier,
                                    literal_eval(r_jan['click_values']),
                                    r_jan['input_values'],
                                    result_jan.student,
                                    survey_type,
                                    transformation_jan,
                                )
                                survey_student_result_jan_nt = common_util.calc_survey_results(
                                    jan_identifier,
                                    literal_eval(r_jan['click_values']),
                                    r_jan['input_values'],
                                    result_jan.student,
                                    survey_type,
                                ) 

                                if not survey_student_result_jan[0] == '':
                                    ws.cell('D' + str(index)).value = survey_student_result_jan[0]
                                    if not survey_student_result_sept[0] == '':
                                        diff = int(survey_student_result_jan[0]) - int(survey_student_result_sept[0])
                                        ws.cell('E' + str(index)).value = diff
                                    ws.cell('G' + str(index)).value = survey_student_result_jan_nt[0]
                            except Exception as e:
                                print('Jan' + str(e))
                        
                        index += 1
                        

        
    
    wb.save(filename = '/tmp/audun.xlsx')
#    wb.save(response)

#    return response

def excel_for_principals(school_id):
    ref_values = {
        1:  (20, 55, 75),
        2:  (40, 85, 100),
        3:  (55, 100, 120),
        4:  (80, 120, 145),
        5:  (90, 140, 160),
        6:  (105, 155, 175),
        7:  (120, 165, 190),
        8:  (130, 180, 210),
        9:  (140, 180, 210),
        10: (145, 180, 210),
    }

    wb = openpyxl.Workbook()
    ws = wb.get_active_sheet()
    wb.remove_sheet(ws)     
    # Get the school object
    school = School.objects.get(id = school_id)

    tests = (
        ('b{}_LF_jan17', 'Janúar 2017'),
        ('{}b_LF_sept', 'September 2016'),
    )
    for test in tests:
        identifier = test[0]
        title = test[1]
        ws = wb.create_sheet(title = title)
        ws['A1'] = 'Bekkur'
        ws['B1'] = 'Fjöldi nemenda'
        ws['C1'] = 'Fjöldi nemenda sem þreytti próf'
        ws['D1'] = 'Hlutfall sem nær 90% viðmiðum'
        ws['E1'] = 'Hlutfall sem nær 50% viðmiðum'
        ws['F1'] = 'Hlutfall sem nær 25% viðmiðum'
        index = 2
        errors = []
        for year in range(1,11):
            ws['A' + str(index)] = year
            survey = Survey.objects.filter(identifier = identifier.format(year)).first()
            survey_type = SurveyType.objects.filter(survey=survey.id).values('id')
            dic = survey_type[0]
            survey_type = dic['id']
            transformation = SurveyTransformation.objects.filter(survey=survey)
            studentgroups = StudentGroup.objects.filter(school = school, student_year = year).all()
            this_year_result = {
                'students': 0,
                'students_who_took_test': 0,
                'students_over_25pct': 0,
                'students_over_50pct': 0,
                'students_over_90pct': 0,
            }
            for studentgroup in studentgroups:
                this_year_result['students'] += studentgroup.students.all().count()
                groupsurveys = GroupSurvey.objects.filter(studentgroup = studentgroup, survey = survey)
                if groupsurveys.all().count() > 1:
                    errors.append('sama próf skráð {} sinnum fyrir {}'.format(groupsurveys.all().count(), studentgroup.name))
                for groupsurvey in groupsurveys.all():
                    for student in studentgroup.students.all():
                        surveyresults = SurveyResult.objects.filter(survey = groupsurvey, student = student)
                        if surveyresults.all().count() > 1:
                            errors.append('{} niðurstöður í sama prófi skráðar fyrir nemanda {} í bekk {}'.format(
                                surveyresults.all().count(),
                                student.ssn,
                                studentgroup.name,
                            ))
                        for surveyresult in surveyresults.all():
                            r = literal_eval(surveyresult.results)  # get student results
                            try:
                                survey_student_result = common_util.calc_survey_results(
                                    survey_identifier = identifier,
                                    click_values = literal_eval(r['click_values']),
                                    input_values = r['input_values'],
                                    student = student,
                                    survey_type = survey_type,
                                    transformation = transformation,
                                )
                                #import pdb; pdb.set_trace()
                                if not survey_student_result[0] == '':
                                    this_year_result['students_who_took_test'] += 1
                                    if int(survey_student_result[0]) >= ref_values[year][2]:
                                        this_year_result['students_over_25pct'] += 1
                                    if int(survey_student_result[0]) >= ref_values[year][1]:
                                        this_year_result['students_over_50pct'] += 1
                                    if int(survey_student_result[0]) >= ref_values[year][0]:
                                        this_year_result['students_over_90pct'] += 1
                            except:
                                pass

            ws['B' + str(index)] = this_year_result['students']
            ws['C' + str(index)] = this_year_result['students_who_took_test']
            if this_year_result['students'] > 0:
                pct_over_90pct = (this_year_result['students_over_90pct'] / this_year_result['students']) * 100
                ws['D' + str(index)] = pct_over_90pct

                pct_over_50pct = (this_year_result['students_over_50pct'] / this_year_result['students']) * 100
                ws['E' + str(index)] = pct_over_50pct

                pct_over_25pct = (this_year_result['students_over_25pct'] / this_year_result['students']) * 100
                ws['F' + str(index)] = pct_over_25pct

            else:
                ws['D' + str(index)] = 0
                ws['E' + str(index)] = 0
                ws['F' + str(index)] = 0

            index += 1
        dims = {}
        for row in ws.rows:
            for cell in row:
                if cell.value:
                    dims[cell.column] = max((dims.get(cell.column, 0), len(str(cell.value))))
        for col, value in dims.items():
            ws.column_dimensions[col].width = int(value) + 2

        chart = AreaChart()
        chart.title = "Lesfimi í {} - {}".format(title, school.name)
        chart.style = 10
        chart.width = 40
        chart.height = 20

        chart.x_axis.title = 'Bekkur'
        chart.y_axis.title = 'Prósent'

        cats = Reference(ws, min_col=1, min_row=2, max_row=index - 1)
        data = Reference(ws, min_col=4, min_row=1, max_col=6, max_row=index)
        chart.add_data(data, titles_from_data=True)
        chart.set_categories(cats)

        if errors:
            index += 1
            for error in errors:
                ws['A' + str(index)] = "ATH: " + error
                ws['A' + str(index)].fill = PatternFill(start_color='ff0000', end_color='ff0000', fill_type='solid')
                ws.merge_cells('A' + str(index) + ':F' + str(index))
                index += 1

        ws.add_chart(chart, "A" + str(index + 2))

    wb.save(filename='/tmp/test.xlsx')
