# -*- coding: utf-8 -*-
from django.http import HttpResponse

from ast import literal_eval

import openpyxl
from openpyxl.styles import PatternFill
from openpyxl.chart import AreaChart, BarChart, Reference
from openpyxl.chart.layout import Layout, ManualLayout

from survey.models import (
    Survey,
    SurveyType,
)
from common.models import (
    StudentGroup,
    GroupSurvey,
    SurveyResult,
    SurveyTransformation,
)
import common.util as common_util


def lesfimi_excel_entire_country_stats():
    ref_values = {
        1: (20, 55, 75),
        2: (40, 85, 100),
        3: (55, 100, 120),
        4: (80, 120, 145),
        5: (90, 140, 160),
        6: (105, 155, 175),
        7: (120, 165, 190),
        8: (130, 180, 210),
        9: (140, 180, 210),
        10: (145, 180, 210),
    }

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=Lesfimi - Allt Landið.xlsx'

    wb = openpyxl.Workbook()
    ws = wb.get_active_sheet()
    wb.remove_sheet(ws)

    tests = (
        ('b{}_LF_jan17', 'Janúar 2017'),
        ('{}b_LF_sept', 'September 2016'),
    )
    for test in tests:
        identifier = test[0]
        title = test[1]
        ws = wb.create_sheet(title=title)
        ws['A1'] = 'Árgangur'
        ws['B1'] = 'Fjöldi nemenda'
        ws['C1'] = 'Fjöldi sem þreytti próf'
        ws['D1'] = 'Hlutfall sem þreytti próf'
        ws['E1'] = 'Hlutfall sem nær 90% viðmiðum'
        ws['F1'] = 'Hlutfall sem nær 50% viðmiðum'
        ws['G1'] = 'Hlutfall sem nær 25% viðmiðum'
        index = 2
        errors = []
        for year in range(1, 11):
            ws['A' + str(index)] = year
            survey = Survey.objects.filter(identifier=identifier.format(year)).first()
            survey_type = SurveyType.objects.filter(survey=survey.id).values('id')
            dic = survey_type[0]
            survey_type = dic['id']
            transformation = SurveyTransformation.objects.filter(survey=survey)
            studentgroups = StudentGroup.objects.filter(student_year=year).all()
            this_year_result = {
                'students': 0,
                'students_who_took_test': 0,
                'students_over_25pct': 0,
                'students_over_50pct': 0,
                'students_over_90pct': 0,
            }
            for studentgroup in studentgroups:
                this_year_result['students'] += studentgroup.students.all().count()
                groupsurveys = GroupSurvey.objects.filter(studentgroup=studentgroup, survey=survey)
                if groupsurveys.all().count() > 1:
                    errors.append('sama próf skráð {} sinnum fyrir {} í {}'.format(
                        groupsurveys.all().count(), studentgroup.name, studentgroup.school.name))
                for groupsurvey in groupsurveys.all():
                    for student in studentgroup.students.all():
                        surveyresults = SurveyResult.objects.filter(survey=groupsurvey, student=student)
                        if surveyresults.all().count() > 1:
                            errors.append('{} niðurstöður í sama prófi skráðar fyrir nemanda {} í bekk {} í {}'.format(
                                surveyresults.all().count(),
                                student.ssn,
                                studentgroup.name,
                                studentgroup.school.name,
                            ))
                        for surveyresult in surveyresults.all():
                            r = literal_eval(surveyresult.results)  # get student results
                            try:
                                survey_student_result = common_util.calc_survey_results(
                                    survey_identifier=identifier,
                                    click_values=literal_eval(r['click_values']),
                                    input_values=r['input_values'],
                                    student=student,
                                    survey_type=survey_type,
                                    transformation=transformation,
                                )
                                # import pdb; pdb.set_trace()
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
            if this_year_result['students'] > 0 and this_year_result['students_who_took_test'] > 0:
                ws['D' + str(index)] = (this_year_result['students_who_took_test'] / this_year_result['students']) * 100
                pct_over_90pct = (this_year_result['students_over_90pct'] /
                                  this_year_result['students_who_took_test']) * 100
                ws['E' + str(index)] = pct_over_90pct

                pct_over_50pct = (this_year_result['students_over_50pct'] /
                                  this_year_result['students_who_took_test']) * 100
                ws['F' + str(index)] = pct_over_50pct

                pct_over_25pct = (this_year_result['students_over_25pct'] /
                                  this_year_result['students_who_took_test']) * 100
                ws['G' + str(index)] = pct_over_25pct

            else:
                ws['D' + str(index)] = 0
                ws['E' + str(index)] = 0
                ws['F' + str(index)] = 0
                ws['G' + str(index)] = 0

            index += 1
        dims = {}
        for row in ws.rows:
            for cell in row:
                if cell.value:
                    dims[cell.column] = max((dims.get(cell.column, 0), len(str(cell.value))))
        for col, value in dims.items():
            ws.column_dimensions[col].width = int(value) + 2

        chart = AreaChart()
        chart.title = "Lesfimi í {} - Allt landið".format(title)
        chart.style = 10
        chart.width = 40
        chart.height = 20

        chart.layout = Layout(
            ManualLayout(
                xMode="edge",
                yMode="edge",
            )
        )

        chart.x_axis.title = 'Árgangur'
        chart.y_axis.title = 'Prósent'

        chart.y_axis.scaling.min = 0
        chart.y_axis.scaling.max = 100

        cats = Reference(ws, min_col=1, min_row=2, max_row=index - 1)
        data = Reference(ws, min_col=5, min_row=1, max_col=7, max_row=index)
        chart.add_data(data, titles_from_data=True)
        chart.set_categories(cats)

        bchart = BarChart()
        bchart.title = "Hlutfall nemenda sem þreyttu próf"
        bchart.style = 10
        bchart.width = 20
        bchart.height = 10

        bchart.x_axis.title = 'Árgangur'
        bchart.y_axis.title = 'Prósent'

        bchart.y_axis.scaling.min = 0
        bchart.y_axis.scaling.max = 100

        bdata = Reference(ws, min_col=4, max_col=4, min_row=2, max_row=index)
        bchart.add_data(bdata)
        bchart.legend = None
        bchart.set_categories(cats)
        ws.add_chart(bchart, "I1")

        if index > 20:
            ws.add_chart(chart, "A" + str(index + 2))
        else:
            ws.add_chart(chart, "A22")

        if errors:
            ws = wb.create_sheet(title='Villur')
            index = 1
            for error in errors:
                ws['A' + str(index)] = "ATH: " + error
                ws['A' + str(index)].fill = PatternFill(start_color='ff0000', end_color='ff0000', fill_type='solid')
                ws.merge_cells('A' + str(index) + ':F' + str(index))
                index += 1

    wb.save(filename='/tmp/test.xlsx')
    # wb.save(response)

    return response


def _lesfimi_excel_result_duplicates():
    wb = openpyxl.Workbook()
    ws = wb.get_active_sheet()
    wb.remove_sheet(ws)

    tests = (
        ('b{}_LF_jan17', 'Janúar 2017'),
        ('{}b_LF_sept', 'September 2016'),
    )
    for test in tests:
        identifier = test[0]
        title = test[1]
        ws = wb.create_sheet(title=title)
        ws['A1'] = 'Kennitala'
        ws['B1'] = 'Groupsurvey id'
        ws['C1'] = 'Surveyresult id'
        ws['D1'] = 'Result'
        index = 2
        errors = []
        for year in range(1, 11):
            ws['A' + str(index)] = year
            survey = Survey.objects.filter(identifier=identifier.format(year)).first()
            survey_type = SurveyType.objects.filter(survey=survey.id).values('id')
            dic = survey_type[0]
            survey_type = dic['id']
            studentgroups = StudentGroup.objects.filter(student_year=year).all()
            for studentgroup in studentgroups:
                groupsurveys = GroupSurvey.objects.filter(studentgroup=studentgroup, survey=survey)
                if groupsurveys.all().count() > 1:
                    errors.append('sama próf skráð {} sinnum fyrir {} í {}'.format(
                        groupsurveys.all().count(), studentgroup.name, studentgroup.school.name))
                for groupsurvey in groupsurveys.all():
                    for student in studentgroup.students.all():
                        surveyresults = SurveyResult.objects.filter(survey=groupsurvey, student=student)
                        if surveyresults.all().count() > 1:
                            for surveyresult in surveyresults.all():
                                ws['A' + str(index)] = student.ssn
                                ws['B' + str(index)] = groupsurvey.id
                                ws['C' + str(index)] = surveyresult.id
                                ws['D' + str(index)] = surveyresult.results
                                index += 1

    wb.save(filename='/tmp/duplicates.xlsx')


def _generate_excel_audun():
    # def admin_output_excel(request):

    # response = HttpResponse(
    # content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    # response['Content-Disposition'] = 'attachment; filename=Þjálguðgögn.xlsx'

    wb = openpyxl.Workbook()

    ws = wb.get_active_sheet()
    wb.remove_sheet(ws)
    for year in range(1, 11):
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
        surveys = Survey.objects.filter(survey_type_id=2, student_year=year, identifier=sept_identifier)
        groups = StudentGroup.objects.filter(student_year=year).all()
        for survey in surveys:
            survey_type = SurveyType.objects.filter(survey=survey.id).values('id')
            dic = survey_type[0]
            survey_type = dic['id']
            transformation_sept = SurveyTransformation.objects.filter(survey=survey)
            for group in groups:
                groupsurveys = GroupSurvey.objects.filter(studentgroup=group, survey=survey).all()
                for groupsurvey in groupsurveys:
                    results = SurveyResult.objects.filter(survey=groupsurvey)
                    for result_sept in results:
                        ws.cell('A' + str(index)).value = result_sept.student.ssn
                        ws.cell('B' + str(index)).value = result_sept.student.name
                        try:
                            r_sept = literal_eval(result_sept.results)
                            try:
                                click_values = literal_eval(r_sept['click_values'])
                            except:
                                click_values = []
                            survey_student_result_sept = common_util.calc_survey_results(
                                sept_identifier,
                                click_values,
                                r_sept['input_values'],
                                result_sept.student,
                                survey_type,
                                transformation_sept,
                            )
                            survey_student_result_sept_nt = common_util.calc_survey_results(
                                sept_identifier,
                                click_values,
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
                        jan_survey = Survey.objects.filter(identifier=jan_identifier).first()
                        transformation_jan = SurveyTransformation.objects.filter(survey=jan_survey)
                        jan_gs = GroupSurvey.objects.filter(
                            survey=jan_survey, studentgroup=groupsurvey.studentgroup).first()
                        # import pdb; pdb.set_trace()

                        if SurveyResult.objects.filter(student=result_sept.student, survey=jan_gs).exists():
                            result_jan = SurveyResult.objects.filter(student=result_sept.student, survey=jan_gs).first()
                            try:
                                r_jan = literal_eval(result_jan.results)
                                try:
                                    click_values = literal_eval(r_jan['click_values'])
                                except:
                                    click_values = []
                                survey_student_result_jan = common_util.calc_survey_results(
                                    jan_identifier,
                                    click_values,
                                    r_jan['input_values'],
                                    result_jan.student,
                                    survey_type,
                                    transformation_jan,
                                )
                                survey_student_result_jan_nt = common_util.calc_survey_results(
                                    jan_identifier,
                                    click_values,
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
        dims = {}
        for row in ws.rows:
            for cell in row:
                if cell.value:
                    dims[cell.column] = max((dims.get(cell.column, 0), len(str(cell.value))))
        for col, value in dims.items():
            ws.column_dimensions[col].width = int(value) + 2

    wb.save(filename='/tmp/audun.xlsx')
#    wb.save(response)

#    return response
