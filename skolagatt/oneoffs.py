# -*- coding: utf-8 -*-
from django.http import HttpResponse

from ast import literal_eval

import openpyxl
from openpyxl.styles import PatternFill
from openpyxl.chart import AreaChart, BarChart, Reference
from openpyxl.chart.layout import Layout, ManualLayout

from survey.models import (
    Survey,
)
from common.models import (
    School,
    StudentGroup,
    GroupSurvey,
    SurveyResult,
)


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
        ('b{}_LF_mai17', 'Maí 2017'),
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
                            try:
                                survey_student_result = surveyresult.calculated_results()
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


def _samraemd_excel_maeting():
    wb = openpyxl.Workbook()
    ws = wb.get_active_sheet()

    schools = School.objects.all()
    surveys = Survey.objects.filter(
        identifier__in=['SKP109', 'SKP110', 'SKP209', 'SKP210'],
    )
    ws['A1'] = 'Kennitala'
    ws['B1'] = 'Skóli'
    ws['C1'] = 'Skólanúmer'
    ws['D1'] = 'Próf'
    ws['E1'] = 'Kóði'
    ws['F1'] = 'Staða'

    index = 2
    for school in schools:
        studentgroups = StudentGroup.objects.filter(
            school=school,
            student_year__in=['9', '10'],
        ).all()
        for studentgroup in studentgroups:
            groupsurveys = GroupSurvey.objects.filter(
                studentgroup=studentgroup,
                survey__in=surveys,
            ).all()
            for groupsurvey in groupsurveys:
                survey_results = SurveyResult.objects.filter(
                    survey=groupsurvey,
                ).all()
                for sr in survey_results:
                    r = literal_eval(sr.results)
                    ws['A' + str(index)] = sr.student.ssn
                    ws['B' + str(index)] = studentgroup.school.name
                    ws['C' + str(index)] = studentgroup.school.school_nr
                    ws['D' + str(index)] = groupsurvey.survey.identifier
                    try:
                        click_values = literal_eval(r['click_values'])
                        vals = click_values[0].split(',')
                        ws['E' + str(index)] = vals[0]
                        ws['F' + str(index)] = vals[1]
                    except:
                        ws['E' + str(index)] = ''
                    index += 1
    dims = {}
    for row in ws.rows:
        for cell in row:
            if cell.value:
                dims[cell.column] = max((dims.get(cell.column, 0), len(str(cell.value))))
    for col, value in dims.items():
        ws.column_dimensions[col].width = int(value) + 2
    wb.save(filename='/tmp/maeting.xlsx')


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
    tests = [
        ['{}b_LF_sept', 'September 2016', None, None],
        ['b{}_LF_jan17', 'Janúar 2017', None, None],
        ['b{}_LF_mai17', 'Maí 2017', None, None],
    ]

    wb = openpyxl.Workbook()

    ws = wb.get_active_sheet()
    wb.remove_sheet(ws)

    for year in range(1, 11):
        # Get all the surveys
        tests_year = tests
        for i in range(0, len(tests_year)):
            identifier = tests_year[i][0].format(year)
            survey = Survey.objects.get(identifier=identifier)
            tests_year[i][2] = survey

        title = "Árgangur {}".format(year)
        ws = wb.create_sheet(title=title)
        ws['A1'] = 'Kennitala nemanda'
        ws['B1'] = 'Nafn'
        ws['C1'] = 'Nafn skóla'
        ws['D1'] = 'Skóla nr'
        ws['E1'] = 'September'
        ws['F1'] = 'Janúar'
        ws['G1'] = 'Maí'
        ws['H1'] = 'Mismunur'
        ws['I1'] = 'September óþjálgað'
        ws['J1'] = 'Janúar óþjálgað'
        ws['K1'] = 'Maí óþjálgað'
        index = 2
        groups = StudentGroup.objects.filter(student_year=year).all()
        for group in groups:
            school = group.school
            tests_group = tests_year
            for i in range(0, len(tests_group)):
                survey = tests_group[i][2]
                try:
                    groupsurvey = GroupSurvey.objects.get(studentgroup=group, survey=survey)
                except GroupSurvey.MultipleObjectsReturned:
                    groupsurvey = GroupSurvey.objects.filter(studentgroup=group, survey=survey).first()
                except GroupSurvey.DoesNotExist:
                    groupsurvey = None
                tests_group[i][3] = groupsurvey

            for student in group.students.all():
                ws['A' + str(index)] = student.ssn
                ws['B' + str(index)] = student.name
                ws['C' + str(index)] = school.name
                ws['D' + str(index)] = school.school_nr
                col = ord('E')
                col_nt = ord('I')
                for test in tests_group:
                    groupsurvey = test[3]

                    if groupsurvey:
                        try:
                            result = SurveyResult.objects.get(student=student, survey=groupsurvey)
                            calc_res = result.calculated_results()[0]
                            calc_res_nt = result.calculated_results(use_transformation=False)[0]
                        except SurveyResult.DoesNotExist:
                            calc_res = 'N/A'
                            calc_res_nt = 'N/A'
                        except SurveyResult.MultipleObjectsReturned:
                            result = SurveyResult.objects.filter(
                                student=student,
                                survey=groupsurvey
                            ).order_by('-id')
                            calc_res = result.first().calculated_results()[0]
                            calc_res_nt = result.first().calculated_results(use_transformation=False)[0]
                    else:
                        calc_res = 'N/A'
                        calc_res_nt = 'N/A'

                    ws[chr(col) + str(index)] = calc_res
                    ws[chr(col_nt) + str(index)] = calc_res_nt
                    col += 1
                    col_nt += 1
                last = None
                for c in range(ord('E'), ord('G') + 1).__reversed__():
                    if isinstance(ws[chr(c) + str(index)].value, int):
                        last = c
                        break
                first = None
                if last:
                    for c in range(ord('E'), ord('G') + 1):
                        if isinstance(ws[chr(c) + str(index)].value, int):
                            first = c
                            break
                if first and last:
                    diff = ws[chr(last) + str(index)].value - ws[chr(first) + str(index)].value
                    ws['H' + str(index)] = diff
                else:
                    ws['H' + str(index)] = 'N/A'
                index += 1

        dims = {}
        for row in ws.rows:
            for cell in row:
                if cell.value:
                    dims[cell.column] = max((dims.get(cell.column, 0), len(str(cell.value))))
        for col, value in dims.items():
            ws.column_dimensions[col].width = int(value) + 2

    wb.save(filename='/tmp/lesfimi_hragogn.xlsx')


def initialize_locations():
    """
    This is autogenerated code to update the addresses of schools.
    It was made from an Excel worksheet.
    """
    school = School.objects.filter(school_nr='2236', ssn='6306150890', name__startswith='NÚ').first()
    if school:
        school.address = 'Flatarhraun 3'
        school.post_code = '220'
        school.municipality = 'Hafnarfjarðarkaupstaður'
        school.part = 'Ngr. Reykjavíkur'
        school.save()
    else:
        print("school not found: NÚ")

    school = School.objects.filter(school_nr='3162', ssn='6009052010', name__startswith='Akurskóli').first()
    if school:
        school.address = 'Tjarnarbraut 5'
        school.post_code = '260'
        school.municipality = 'Reykjanesbær'
        school.part = 'Suðurnes'
        school.save()
    else:
        print("school not found: Akurskóli")

    school = School.objects.filter(school_nr='2250', ssn='5104070160', name__startswith='Alþjóðaskólinn á Íslandi').first()
    if school:
        school.address = 'Löngulínu 8'
        school.post_code = '210'
        school.municipality = 'Garðabær'
        school.part = 'Ngr. Reykjavíkur'
        school.save()
    else:
        print("school not found: Alþjóðaskólinn á Íslandi")

    school = School.objects.filter(school_nr='4332', ssn='5106942019', name__startswith='Auðarskóli - grunnskóladeild Búðardal').first()
    if school:
        school.address = 'Miðbraut 10'
        school.post_code = '370'
        school.municipality = 'Dalabyggð'
        school.part = 'Vesturland'
        school.save()
    else:
        print("school not found: Auðarskóli - grunnskóladeild Búðardal")

    school = School.objects.filter(school_nr='1191', ssn='5901820529', name__startswith='Austurbæjarskóli').first()
    if school:
        school.address = 'Vitastíg'
        school.post_code = '101'
        school.municipality = 'Reykjavíkurborg'
        school.part = 'Reykjavík'
        school.save()
    else:
        print("school not found: Austurbæjarskóli")

    school = School.objects.filter(school_nr='2384', ssn='6710882989', name__startswith='Álfhólsskóli').first()
    if school:
        school.address = 'Álfhólsvegi 100'
        school.post_code = '200'
        school.municipality = 'Kópavogsbær'
        school.part = 'Ngr. Reykjavíkur'
        school.save()
    else:
        print("school not found: Álfhólsskóli")

    school = School.objects.filter(school_nr='2246', ssn='6710884769', name__startswith='Álftanesskóli').first()
    if school:
        school.address = 'v/Breiðumýri'
        school.post_code = '225'
        school.municipality = 'Garðabær'
        school.part = 'Ngr. Reykjavíkur'
        school.save()
    else:
        print("school not found: Álftanesskóli")

    school = School.objects.filter(school_nr='1438', ssn='5901820879', name__startswith='Árbæjarskóli').first()
    if school:
        school.address = 'Rofabæ 34'
        school.post_code = '110'
        school.municipality = 'Reykjavíkurborg'
        school.part = 'Reykjavík'
        school.save()
    else:
        print("school not found: Árbæjarskóli")

    school = School.objects.filter(school_nr='7169', ssn='6205982089', name__startswith='Árskógarskóli').first()
    if school:
        school.address = 'Árskógsströnd'
        school.post_code = '621'
        school.municipality = 'Dalvíkurbyggð'
        school.part = 'Norðurland eystra'
        school.save()
    else:
        print("school not found: Árskógarskóli")

    school = School.objects.filter(school_nr='6254', ssn='6710888169', name__startswith='Árskóli').first()
    if school:
        school.address = 'v/Freyjugötu'
        school.post_code = '550'
        school.municipality = 'Sveitarf. Skagafjörður'
        school.part = 'Norðurland vestra'
        school.save()
    else:
        print("school not found: Árskóli")

    school = School.objects.filter(school_nr='1443', ssn='5009871549', name__startswith='Ártúnsskóli').first()
    if school:
        school.address = 'Árkvörn 6'
        school.post_code = '110'
        school.municipality = 'Reykjavíkurborg'
        school.part = 'Reykjavík'
        school.save()
    else:
        print("school not found: Ártúnsskóli")

    school = School.objects.filter(school_nr='2186', ssn='6310022930', name__startswith='Áslandsskóli').first()
    if school:
        school.address = 'Kríuási 1'
        school.post_code = '221'
        school.municipality = 'Hafnarfjarðarkaupstaður'
        school.part = 'Ngr. Reykjavíkur'
        school.save()
    else:
        print("school not found: Áslandsskóli")

    school = School.objects.filter(school_nr='9274', ssn='5607972229', name__startswith='Barnaskólinn á Eyrarbakka og Stokkseyri').first()
    if school:
        school.address = 'Háeyrarvöllum 56'
        school.post_code = '820'
        school.municipality = 'Sveitarfélagið Árborg'
        school.part = 'Suðurland'
        school.save()
    else:
        print("school not found: Barnaskólinn á Eyrarbakka og Stokkseyri")

    school = School.objects.filter(school_nr='9387', ssn='5106024119', name__startswith='Bláskógaskóli - Laugarvatni').first()
    if school:
        school.address = 'Laugarvatn'
        school.post_code = '840'
        school.municipality = 'Bláskógabyggð'
        school.part = 'Suðurland'
        school.save()
    else:
        print("school not found: Bláskógaskóli - Laugarvatni")

    school = School.objects.filter(school_nr='9363', ssn='5106024120', name__startswith='Bláskógaskóli - Reykholti').first()
    if school:
        school.address = 'Reykholti'
        school.post_code = '801'
        school.municipality = 'Bláskógabyggð'
        school.part = 'Suðurland'
        school.save()
    else:
        print("school not found: Bláskógaskóli - Reykholti")

    school = School.objects.filter(school_nr='6198', ssn='4701691769', name__startswith='Blönduskóli').first()
    if school:
        school.address = 'Húnabraut '
        school.post_code = '540'
        school.municipality = 'Blönduósbær'
        school.part = 'Norðurland vestra'
        school.save()
    else:
        print("school not found: Blönduskóli")

    school = School.objects.filter(school_nr='7437', ssn='6710889649', name__startswith='Borgarhólsskóli').first()
    if school:
        school.address = 'Skólagarður 1'
        school.post_code = '640'
        school.municipality = 'Norðurþing'
        school.part = 'Norðurland eystra'
        school.save()
    else:
        print("school not found: Borgarhólsskóli")

    school = School.objects.filter(school_nr='1359', ssn='5901820369', name__startswith='Breiðagerðisskóli').first()
    if school:
        school.address = 'v/Breiðagerði'
        school.post_code = '108'
        school.municipality = 'Reykjavíkurborg'
        school.part = 'Reykjavík'
        school.save()
    else:
        print("school not found: Breiðagerðisskóli")

    school = School.objects.filter(school_nr='1414', ssn='5901820449', name__startswith='Breiðholtsskóli').first()
    if school:
        school.address = 'Arnarbakka 1-3'
        school.post_code = '109'
        school.municipality = 'Reykjavíkurborg'
        school.part = 'Reykjavík'
        school.save()
    else:
        print("school not found: Breiðholtsskóli")

    school = School.objects.filter(school_nr='4142', ssn='4101694449', name__startswith='Brekkubæjarskóli').first()
    if school:
        school.address = 'v/Vesturgötu'
        school.post_code = '300'
        school.municipality = 'Akraneskaupstaður'
        school.part = 'Vesturland'
        school.save()
    else:
        print("school not found: Brekkubæjarskóli")

    school = School.objects.filter(school_nr='7282', ssn='4101696229', name__startswith='Brekkuskóli').first()
    if school:
        school.address = 'v/Skólastíg'
        school.post_code = '600'
        school.municipality = 'Akureyrarkaupstaður'
        school.part = 'Norðurland eystra'
        school.save()
    else:
        print("school not found: Brekkuskóli")

    school = School.objects.filter(school_nr='8149', ssn='4810043220', name__startswith='Brúarásskóli').first()
    if school:
        school.address = 'Brúarás'
        school.post_code = '701'
        school.municipality = 'Fljótsdalshérað'
        school.part = 'Austurland'
        school.save()
    else:
        print("school not found: Brúarásskóli")

    school = School.objects.filter(school_nr='1236', ssn='4310032010', name__startswith='Brúarskóli').first()
    if school:
        school.address = 'Vesturhlíð 5'
        school.post_code = '105'
        school.municipality = 'Reykjavíkurborg'
        school.part = 'Reykjavík'
        school.save()
    else:
        print("school not found: Brúarskóli")

    school = School.objects.filter(school_nr='2235', ssn='5405992039', name__startswith='Barnaskóli Hjallastefnunnar, Hafnarfirði').first()
    if school:
        school.address = 'Hjallabraut 55'
        school.post_code = '220'
        school.municipality = 'Hafnarfjarðarkaupstaður'
        school.part = 'Ngr. Reykjavíkur'
        school.save()
    else:
        print("school not found: Barnaskóli Hjallastefnunnar, Hafnarfirði")

    school = School.objects.filter(school_nr='1170', ssn='5405992039', name__startswith='BSK Reykjavík').first()
    if school:
        school.address = 'Nauthólsvegi 87'
        school.post_code = '101'
        school.municipality = 'Reykjavíkurborg'
        school.part = 'Reykjavík'
        school.save()
    else:
        print("school not found: BSK Reykjavík")

    school = School.objects.filter(school_nr='2247', ssn='5405992039', name__startswith='Barnaskóli Hjallastefnunnar í Garðabæ Vífilsstöðum').first()
    if school:
        school.address = 'Vífilsstaðavegur 123'
        school.post_code = '210'
        school.municipality = 'Garðabær'
        school.part = 'Ngr. Reykjavíkur'
        school.save()
    else:
        print("school not found: Barnaskóli Hjallastefnunnar í Garðabæ Vífilsstöðum")

    school = School.objects.filter(school_nr='1480', ssn='5302697609', name__startswith='Dalskóli').first()
    if school:
        school.address = 'Úlfarsbraut 118-120'
        school.post_code = '113'
        school.municipality = 'Reykjavíkurborg'
        school.part = 'Reykjavík'
        school.save()
    else:
        print("school not found: Dalskóli")

    school = School.objects.filter(school_nr='8183', ssn='6810885209', name__startswith='Egilsstaðaskóli').first()
    if school:
        school.address = 'Tjarnarlönd 11'
        school.post_code = '700'
        school.municipality = 'Fljótsdalshérað'
        school.part = 'Austurland'
        school.save()
    else:
        print("school not found: Egilsstaðaskóli")

    school = School.objects.filter(school_nr='8161', ssn='6810885639', name__startswith='Fellaskóli - Fellahreppi').first()
    if school:
        school.address = 'Einhleypingi'
        school.post_code = '701'
        school.municipality = 'Fljótsdalshérað'
        school.part = 'Austurland'
        school.save()
    else:
        print("school not found: Fellaskóli - Fellahreppi")

    school = School.objects.filter(school_nr='1426', ssn='5901821179', name__startswith='Fellaskóli - Reykjavík').first()
    if school:
        school.address = 'Norðurfelli 17-19'
        school.post_code = '111'
        school.municipality = 'Reykjavíkurborg'
        school.part = 'Reykjavík'
        school.save()
    else:
        print("school not found: Fellaskóli - Reykjavík")

    school = School.objects.filter(school_nr='5353', ssn='5606861109', name__startswith='Finnbogastaðaskóli').first()
    if school:
        school.address = 'Finnbogastöðum'
        school.post_code = '523'
        school.municipality = 'Árneshreppur'
        school.part = 'Vestfirðir'
        school.save()
    else:
        print("school not found: Finnbogastaðaskóli")

    school = School.objects.filter(school_nr='2257', ssn='4702830179', name__startswith='Flataskóli').first()
    if school:
        school.address = 'v/Vífilsstaðaveg'
        school.post_code = '210'
        school.municipality = 'Garðabær'
        school.part = 'Ngr. Reykjavíkur'
        school.save()
    else:
        print("school not found: Flataskóli")

    school = School.objects.filter(school_nr='9252', ssn='6006061310', name__startswith='Flóaskóli').first()
    if school:
        school.address = 'Villingaholti'
        school.post_code = '801'
        school.municipality = 'Flóahreppi'
        school.part = 'Suðurland'
        school.save()
    else:
        print("school not found: Flóaskóli")

    school = School.objects.filter(school_nr='9352', ssn='6401692309', name__startswith='Flúðaskóli').first()
    if school:
        school.address = 'Flúðum'
        school.post_code = '845'
        school.municipality = 'Hrunamannahreppur'
        school.part = 'Suðurland'
        school.save()
    else:
        print("school not found: Flúðaskóli")

    school = School.objects.filter(school_nr='1449', ssn='6708850899', name__startswith='Foldaskóli').first()
    if school:
        school.address = 'Logafold 1'
        school.post_code = '112'
        school.municipality = 'Reykjavíkurborg'
        school.part = 'Reykjavík'
        school.save()
    else:
        print("school not found: Foldaskóli")

    school = School.objects.filter(school_nr='1379', ssn='5901820289', name__startswith='Fossvogsskóli').first()
    if school:
        school.address = 'Haðalandi 26'
        school.post_code = '108'
        school.municipality = 'Reykjavíkurborg'
        school.part = 'Reykjavík'
        school.save()
    else:
        print("school not found: Fossvogsskóli")

    school = School.objects.filter(school_nr='2249', ssn='6710883879', name__startswith='Garðaskóli').first()
    if school:
        school.address = 'v/Vífilsstaðaveg'
        school.post_code = '210'
        school.municipality = 'Garðabær'
        school.part = 'Ngr. Reykjavíkur'
        school.save()
    else:
        print("school not found: Garðaskóli")

    school = School.objects.filter(school_nr='3137', ssn='5701694329', name__startswith='Gerðaskóli').first()
    if school:
        school.address = 'Garðbraut 90'
        school.post_code = '250'
        school.municipality = 'Sveitarfélagið Garður'
        school.part = 'Suðurnes'
        school.save()
    else:
        print("school not found: Gerðaskóli")

    school = School.objects.filter(school_nr='7255', ssn='4101696229', name__startswith='Giljaskóli').first()
    if school:
        school.address = 'v/Kiðagil'
        school.post_code = '603'
        school.municipality = 'Akureyrarkaupstaður'
        school.part = 'Norðurland eystra'
        school.save()
    else:
        print("school not found: Giljaskóli")

    school = School.objects.filter(school_nr='7259', ssn='6710889219', name__startswith='Glerárskóli').first()
    if school:
        school.address = 'v/Höfðahlíð'
        school.post_code = '603'
        school.municipality = 'Akureyrarkaupstaður'
        school.part = 'Norðurland eystra'
        school.save()
    else:
        print("school not found: Glerárskóli")

    school = School.objects.filter(school_nr='1112', ssn='4506861159', name__startswith='Grandaskóli').first()
    if school:
        school.address = 'Keilugranda 2'
        school.post_code = '107'
        school.municipality = 'Reykjavíkurborg'
        school.part = 'Reykjavík'
        school.save()
    else:
        print("school not found: Grandaskóli")

    school = School.objects.filter(school_nr='7369', ssn='6810884079', name__startswith='Grenivíkurskóli').first()
    if school:
        school.address = 'Grenivíkurvegi'
        school.post_code = '610'
        school.municipality = 'Grýtubakkahreppur'
        school.part = 'Norðurland eystra'
        school.save()
    else:
        print("school not found: Grenivíkurskóli")

    school = School.objects.filter(school_nr='7113', ssn='4101696229', name__startswith='Grímseyjarskóli').first()
    if school:
        school.address = 'Miðtúni'
        school.post_code = '611'
        school.municipality = 'Akureyrarkaupstaður'
        school.part = 'Norðurland eystra'
        school.save()
    else:
        print("school not found: Grímseyjarskóli")

    school = School.objects.filter(school_nr='4166', ssn='6710885659', name__startswith='Grundaskóli').first()
    if school:
        school.address = 'Espigrund 1'
        school.post_code = '300'
        school.municipality = 'Akraneskaupstaður'
        school.part = 'Vesturland'
        school.save()
    else:
        print("school not found: Grundaskóli")

    school = School.objects.filter(school_nr='5276', ssn='6710886629', name__startswith='Grunnskóli Bolungarvíkur').first()
    if school:
        school.address = 'Höfðastíg 3-5'
        school.post_code = '415'
        school.municipality = 'Bolungarvíkurkaupstaður'
        school.part = 'Vestfirðir'
        school.save()
    else:
        print("school not found: Grunnskóli Bolungarvíkur")

    school = School.objects.filter(school_nr='4188', ssn='5106942289', name__startswith='Grunnskóli Borgarfjarðar').first()
    if school:
        school.address = 'Hvanneyri'
        school.post_code = '311'
        school.municipality = 'Borgarbyggð'
        school.part = 'Vesturland'
        school.save()
    else:
        print("school not found: Grunnskóli Borgarfjarðar")

    school = School.objects.filter(school_nr='4188', ssn='5106942289', name__startswith='Grunnskóli Borgarfjarðar').first()
    if school:
        school.address = 'Kleppjárnsreykjum'
        school.post_code = '320'
        school.municipality = 'Borgarbyggð'
        school.part = 'Vesturland'
        school.save()
    else:
        print("school not found: Grunnskóli Borgarfjarðar")

    school = School.objects.filter(school_nr='4188', ssn='5106942289', name__startswith='Grunnskóli Borgarfjarðar').first()
    if school:
        school.address = 'Varmalandi'
        school.post_code = '311'
        school.municipality = 'Borgarbyggð'
        school.part = 'Vesturland'
        school.save()
    else:
        print("school not found: Grunnskóli Borgarfjarðar")

    school = School.objects.filter(school_nr='8242', ssn='6810885719', name__startswith='Grunnskóli Borgarfjarðar eystra').first()
    if school:
        school.address = 'Hólalandsvegi'
        school.post_code = '720'
        school.municipality = 'Borgarfjarðarhreppur'
        school.part = 'Austurland'
        school.save()
    else:
        print("school not found: Grunnskóli Borgarfjarðar eystra")

    school = School.objects.filter(school_nr='7147', ssn='6205982089', name__startswith='Dalvíkurskóli').first()
    if school:
        school.address = 'v/Mímisveg'
        school.post_code = '620'
        school.municipality = 'Dalvíkurbyggð'
        school.part = 'Norðurland eystra'
        school.save()
    else:
        print("school not found: Dalvíkurskóli")

    school = School.objects.filter(school_nr='8397', ssn='6810886799', name__startswith='Grunnskóli Djúpavogs').first()
    if school:
        school.address = 'Vörðu 6'
        school.post_code = '765'
        school.municipality = 'Djúpavogshreppur'
        school.part = 'Austurland'
        school.save()
    else:
        print("school not found: Grunnskóli Djúpavogs")

    school = School.objects.filter(school_nr='8357', ssn='6810886369', name__startswith='Grunnskóli Fáskrúðsfjarðar').first()
    if school:
        school.address = 'Hlíðargötu 56'
        school.post_code = '750'
        school.municipality = 'Fjarðabyggð'
        school.part = 'Austurland'
        school.save()
    else:
        print("school not found: Grunnskóli Fáskrúðsfjarðar")

    school = School.objects.filter(school_nr='6412', ssn='6704100640', name__startswith='Grunnskóli Fjallabyggðar').first()
    if school:
        school.address = 'Tjarnarstíg'
        school.post_code = '625'
        school.municipality = 'Fjallabyggð'
        school.part = 'Norðurland vestra'
        school.save()
    else:
        print("school not found: Grunnskóli Fjallabyggðar")

    school = School.objects.filter(school_nr='6412', ssn='6704100640', name__startswith='Grunnskóli Fjallabyggðar').first()
    if school:
        school.address = 'Norðurgata'
        school.post_code = '580'
        school.municipality = 'Fjallabyggð'
        school.part = 'Norðurland vestra'
        school.save()
    else:
        print("school not found: Grunnskóli Fjallabyggðar")

    school = School.objects.filter(school_nr='6412', ssn='6704100640', name__startswith='Grunnskóli Fjallabyggðar').first()
    if school:
        school.address = 'Hlíðarvegur'
        school.post_code = '580'
        school.municipality = 'Fjallabyggð'
        school.part = 'Norðurland vestra'
        school.save()
    else:
        print("school not found: Grunnskóli Fjallabyggðar")

    school = School.objects.filter(school_nr='3114', ssn='6710884419', name__startswith='Grunnskóli Grindavíkur').first()
    if school:
        school.address = 'Skólabraut 1'
        school.post_code = '240'
        school.municipality = 'Grindavíkurbær'
        school.part = 'Suðurnes'
        school.save()
    else:
        print("school not found: Grunnskóli Grindavíkur")

    school = School.objects.filter(school_nr='4289', ssn='4401692529', name__startswith='Grunnskóli Grundarfjarðar').first()
    if school:
        school.address = 'Borgarbraut 19'
        school.post_code = '350'
        school.municipality = 'Grundarfjarðarbær'
        school.part = 'Vesturland'
        school.save()
    else:
        print("school not found: Grunnskóli Grundarfjarðar")

    school = School.objects.filter(school_nr='8429', ssn='4902830219', name__startswith='Grunnskóli Hornafjarðar').first()
    if school:
        school.address = 'Svalbarði 6 og Víkurbraut 9'
        school.post_code = '780'
        school.municipality = 'Sveitarfélagið Hornafjörður'
        school.part = 'Austurland'
        school.save()
    else:
        print("school not found: Grunnskóli Hornafjarðar")

    school = School.objects.filter(school_nr='6176', ssn='4908992359', name__startswith='Grunnskóli Húnaþings vestra').first()
    if school:
        school.address = 'Borðeyri'
        school.post_code = '500'
        school.municipality = 'Bæjarhreppur'
        school.part = 'Norðurland vestra'
        school.save()
    else:
        print("school not found: Grunnskóli Húnaþings vestra")

    school = School.objects.filter(school_nr='6176', ssn='4908992359', name__startswith='Grunnskóli Húnaþings vestra').first()
    if school:
        school.address = 'Skólavegi 2'
        school.post_code = '530'
        school.municipality = 'Húnaþing vestra'
        school.part = 'Norðurland vestra'
        school.save()
    else:
        print("school not found: Grunnskóli Húnaþings vestra")

    school = School.objects.filter(school_nr='7456', ssn='6401695599', name__startswith='Grunnskóli Raufarhafnar').first()
    if school:
        school.address = 'Skólabraut '
        school.post_code = '675'
        school.municipality = 'Norðurþing'
        school.part = 'Norðurland eystra'
        school.save()
    else:
        print("school not found: Grunnskóli Raufarhafnar")

    school = School.objects.filter(school_nr='8334', ssn='6811886289', name__startswith='Grunnskóli Reyðarfjarðar').first()
    if school:
        school.address = 'Heiðarvegur 14a'
        school.post_code = '730'
        school.municipality = 'Fjarðabyggð'
        school.part = 'Austurland'
        school.save()
    else:
        print("school not found: Grunnskóli Reyðarfjarðar")

    school = School.objects.filter(school_nr='2424', ssn='5208043230', name__startswith='Grunnskóli Seltjarnarness').first()
    if school:
        school.address = 'Nesvegur'
        school.post_code = '170'
        school.municipality = 'Seltjarnarnesbær'
        school.part = 'Ngr. Reykjavíkur'
        school.save()
    else:
        print("school not found: Grunnskóli Seltjarnarness")

    school = School.objects.filter(school_nr='2424', ssn='5208043230', name__startswith='Grunnskóli Seltjarnarness').first()
    if school:
        school.address = 'Skólabraut '
        school.post_code = '170'
        school.municipality = 'Seltjarnarnesbær'
        school.part = 'Ngr. Reykjavíkur'
        school.save()
    else:
        print("school not found: Grunnskóli Seltjarnarness")

    school = School.objects.filter(school_nr='4278', ssn='6710886389', name__startswith='Grunnskóli Snæfellsbæjar - Hellissandi').first()
    if school:
        school.address = 'Keflavíkurgötu 2'
        school.post_code = '360'
        school.municipality = 'Snæfellsbær'
        school.part = 'Vesturland'
        school.save()
    else:
        print("school not found: Grunnskóli Snæfellsbæjar - Hellissandi")

    school = School.objects.filter(school_nr='4278', ssn='6710885739', name__startswith='Grunnskóli Snæfellsbæjar - Lýsuhóli').first()
    if school:
        school.address = 'Lýsuhóli, Staðarsveit'
        school.post_code = '355'
        school.municipality = 'Snæfellsbær'
        school.part = 'Vesturland'
        school.save()
    else:
        print("school not found: Grunnskóli Snæfellsbæjar - Lýsuhóli")

    school = School.objects.filter(school_nr='4278', ssn='6710885739', name__startswith='Grunnskóli Snæfellsbæjar - Ólafsvík').first()
    if school:
        school.address = 'Ennisbraut 11'
        school.post_code = '355'
        school.municipality = 'Snæfellsbær'
        school.part = 'Vesturland'
        school.save()
    else:
        print("school not found: Grunnskóli Snæfellsbæjar - Ólafsvík")

    school = School.objects.filter(school_nr='9471', ssn='6810887339', name__startswith='Grunnskóli Vestmannaeyja').first()
    if school:
        school.address = 'Barnaskólinn/Skólavegi'
        school.post_code = '900'
        school.municipality = 'Vestmannaeyjabær'
        school.part = 'Suðurland'
        school.save()
    else:
        print("school not found: Grunnskóli Vestmannaeyja")

    school = School.objects.filter(school_nr='5152', ssn='4810992859', name__startswith='Grunnskóli Vesturbyggðar').first()
    if school:
        school.address = 'Barðaströnd'
        school.post_code = '451'
        school.municipality = 'Vesturbyggð'
        school.part = 'Vestfirðir'
        school.save()
    else:
        print("school not found: Grunnskóli Vesturbyggðar")

    school = School.objects.filter(school_nr='5152', ssn='5106942369', name__startswith='Bíldudalsskóli').first()
    if school:
        school.address = 'Dalbraut 2'
        school.post_code = '465'
        school.municipality = 'Vesturbyggð'
        school.part = 'Vestfirðir'
        school.save()
    else:
        print("school not found: Bíldudalsskóli")

    school = School.objects.filter(school_nr='5152', ssn='4810992859', name__startswith='Grunnskóli Vesturbyggðar - Patreksskóli').first()
    if school:
        school.address = 'Aðalstræti 53'
        school.post_code = '450'
        school.municipality = 'Vesturbyggð'
        school.part = 'Vestfirðir'
        school.save()
    else:
        print("school not found: Grunnskóli Vesturbyggðar - Patreksskóli")

    school = School.objects.filter(school_nr='5253', ssn='6710887439', name__startswith='Grunnskóli Önundarfjarðar').first()
    if school:
        school.address = 'Tjarnargötu'
        school.post_code = '425'
        school.municipality = 'Ísafjarðarbær'
        school.part = 'Vestfirðir'
        school.save()
    else:
        print("school not found: Grunnskóli Önundarfjarðar")

    school = School.objects.filter(school_nr='7451', ssn='6401695599', name__startswith='Öxarfjarðarskóli, Norðurþingi').first()
    if school:
        school.address = 'Lundi'
        school.post_code = '671'
        school.municipality = 'Norðurþing'
        school.part = 'Norðurland eystra'
        school.save()
    else:
        print("school not found: Öxarfjarðarskóli, Norðurþingi")

    school = School.objects.filter(school_nr='6378', ssn='5506982349', name__startswith='Grunnskólinn austan Vatna').first()
    if school:
        school.address = 'Skólagötu'
        school.post_code = '565'
        school.municipality = 'Sveitarf. Skagafjörður'
        school.part = 'Norðurland vestra'
        school.save()
    else:
        print("school not found: Grunnskólinn austan Vatna")

    school = School.objects.filter(school_nr='6378', ssn='5506982349', name__startswith='Grunnskólinn austan Vatna').first()
    if school:
        school.address = 'Hólum'
        school.post_code = '551'
        school.municipality = 'Sveitarf. Skagafjörður'
        school.part = 'Norðurland vestra'
        school.save()
    else:
        print("school not found: Grunnskólinn austan Vatna")

    school = School.objects.filter(school_nr='6378', ssn='5506982349', name__startswith='Grunnskólinn austan Vatna').first()
    if school:
        school.address = 'Sólgörðum'
        school.post_code = '570'
        school.municipality = 'Sveitarf. Skagafjörður'
        school.part = 'Norðurland vestra'
        school.save()
    else:
        print("school not found: Grunnskólinn austan Vatna")

    school = School.objects.filter(school_nr='8116', ssn='6810885399', name__startswith='Grunnskólinn á Bakkafirði').first()
    if school:
        school.address = 'Skólagötu 5'
        school.post_code = '685'
        school.municipality = 'Langanesbyggð'
        school.part = 'Austurland'
        school.save()
    else:
        print("school not found: Grunnskólinn á Bakkafirði")

    school = School.objects.filter(school_nr='5377', ssn='6710887519', name__startswith='Grunnskólinn á Drangsnesi').first()
    if school:
        school.address = 'Aðalbraut 10'
        school.post_code = '520'
        school.municipality = 'Kaldrananeshreppur'
        school.part = 'Vestfirðir'
        school.save()
    else:
        print("school not found: Grunnskólinn á Drangsnesi")

    school = School.objects.filter(school_nr='8328', ssn='6810885129', name__startswith='Grunnskólinn á Eskifirði').first()
    if school:
        school.address = 'Lambeyrarbraut 16'
        school.post_code = '735'
        school.municipality = 'Fjarðabyggð'
        school.part = 'Austurland'
        school.save()
    else:
        print("school not found: Grunnskólinn á Eskifirði")

    school = School.objects.filter(school_nr='5388', ssn='6710887789', name__startswith='Grunnskólinn á Hólmavík').first()
    if school:
        school.address = 'Skólabraut 20'
        school.post_code = '510'
        school.municipality = 'Strandabyggð'
        school.part = 'Vestfirðir'
        school.save()
    else:
        print("school not found: Grunnskólinn á Hólmavík")

    school = School.objects.filter(school_nr='5287', ssn='6710886549', name__startswith='Grunnskólinn á Ísafirði').first()
    if school:
        school.address = 'Austurvegi 6'
        school.post_code = '400'
        school.municipality = 'Ísafjarðarbær'
        school.part = 'Vestfirðir'
        school.save()
    else:
        print("school not found: Grunnskólinn á Ísafirði")

    school = School.objects.filter(school_nr='5264', ssn='5606861459', name__startswith='Grunnskólinn á Suðureyri').first()
    if school:
        school.address = 'Túngötu 8'
        school.post_code = '430'
        school.municipality = 'Ísafjarðarbær'
        school.part = 'Vestfirðir'
        school.save()
    else:
        print("school not found: Grunnskólinn á Suðureyri")

    school = School.objects.filter(school_nr='5163', ssn='5405992039', name__startswith='Grunnskólinn á Tálknafirði').first()
    if school:
        school.address = 'Sveinseyri'
        school.post_code = '460'
        school.municipality = 'Tálknafjarðarhreppur'
        school.part = 'Vestfirðir'
        school.save()
    else:
        print("school not found: Grunnskólinn á Tálknafirði")

    school = School.objects.filter(school_nr='5197', ssn='5606861299', name__startswith='Grunnskólinn á Þingeyri').first()
    if school:
        school.address = 'Fjarðargötu 24'
        school.post_code = '470'
        school.municipality = 'Ísafjarðarbær'
        school.part = 'Vestfirðir'
        school.save()
    else:
        print("school not found: Grunnskólinn á Þingeyri")

    school = School.objects.filter(school_nr='7478', ssn='4203691749', name__startswith='Grunnskólinn á Þórshöfn').first()
    if school:
        school.address = 'Langanesvegi 20'
        school.post_code = '680'
        school.municipality = 'Langanesbyggð'
        school.part = 'Norðurland eystra'
        school.save()
    else:
        print("school not found: Grunnskólinn á Þórshöfn")

    school = School.objects.filter(school_nr='9196', ssn='4111800189', name__startswith='Grunnskólinn Hellu').first()
    if school:
        school.address = 'Útskálum 6'
        school.post_code = '850'
        school.municipality = 'Rangárþing ytra'
        school.part = 'Suðurland'
        school.save()
    else:
        print("school not found: Grunnskólinn Hellu")

    school = School.objects.filter(school_nr='4217', ssn='6710885819', name__startswith='Grunnskólinn í Borgarnesi').first()
    if school:
        school.address = 'Gunnlaugsgötu 13'
        school.post_code = '310'
        school.municipality = 'Borgarbyggð'
        school.part = 'Vesturland'
        school.save()
    else:
        print("school not found: Grunnskólinn í Borgarnesi")

    school = School.objects.filter(school_nr='8374', ssn='6810886529', name__startswith='Grunnskólinn í Breiðdalshreppi').first()
    if school:
        school.address = 'Selnesi 25'
        school.post_code = '760'
        school.municipality = 'Breiðdalshreppur'
        school.part = 'Austurland'
        school.save()
    else:
        print("school not found: Grunnskólinn í Breiðdalshreppi")

    school = School.objects.filter(school_nr='8471', ssn='6810887259', name__startswith='Grunnskólinn í Hofgarði').first()
    if school:
        school.address = 'Öræfum'
        school.post_code = '785'
        school.municipality = 'Sveitarfélagið Hornafjörður'
        school.part = 'Austurland'
        school.save()
    else:
        print("school not found: Grunnskólinn í Hofgarði")

    school = School.objects.filter(school_nr='7181', ssn='4101696229', name__startswith='Hríseyjarskóli').first()
    if school:
        school.address = 'v/Hólabraut'
        school.post_code = '630'
        school.municipality = 'Akureyrarkaupstaður'
        school.part = 'Norðurland eystra'
        school.save()
    else:
        print("school not found: Hríseyjarskóli")

    school = School.objects.filter(school_nr='9431', ssn='4710882509', name__startswith='Grunnskólinn í Hveragerði').first()
    if school:
        school.address = 'Skólamörk 6'
        school.post_code = '810'
        school.municipality = 'Hveragerðisbær'
        school.part = 'Suðurland'
        school.save()
    else:
        print("school not found: Grunnskólinn í Hveragerði")

    school = School.objects.filter(school_nr='3126', ssn='6710885229', name__startswith='Grunnskólinn í Sandgerði').first()
    if school:
        school.address = 'Skólastræti'
        school.post_code = '245'
        school.municipality = 'Sandgerðisbær'
        school.part = 'Suðurnes'
        school.save()
    else:
        print("school not found: Grunnskólinn í Sandgerði")

    school = School.objects.filter(school_nr='4311', ssn='6710886039', name__startswith='Grunnskólinn í Stykkishólmi').first()
    if school:
        school.address = 'v/Borgarbraut'
        school.post_code = '340'
        school.municipality = 'Stykkishólmsbær'
        school.part = 'Vesturland'
        school.save()
    else:
        print("school not found: Grunnskólinn í Stykkishólmi")

    school = School.objects.filter(school_nr='9453', ssn='4203697009', name__startswith='Grunnskólinn í Þorlákshöfn').first()
    if school:
        school.address = 'Egilsbraut 35'
        school.post_code = '815'
        school.municipality = 'Sveitarfélagið Ölfus'
        school.part = 'Suðurland'
        school.save()
    else:
        print("school not found: Grunnskólinn í Þorlákshöfn")

    school = School.objects.filter(school_nr='1134', ssn='5901821849', name__startswith='Hagaskóli').first()
    if school:
        school.address = 'Fornhaga 1'
        school.post_code = '107'
        school.municipality = 'Reykjavíkurborg'
        school.part = 'Reykjavík'
        school.save()
    else:
        print("school not found: Hagaskóli")

    school = School.objects.filter(school_nr='1454', ssn='5302697609', name__startswith='Hamraskóli').first()
    if school:
        school.address = 'Dyrhömrum 9'
        school.post_code = '112'
        school.municipality = 'Reykjavíkurborg'
        school.part = 'Reykjavík'
        school.save()
    else:
        print("school not found: Hamraskóli")

    school = School.objects.filter(school_nr='3171', ssn='4803160290', name__startswith='Háaleitisskóli Reykjanesbæ').first()
    if school:
        school.address = 'Lindarbraut 624 - Vallarheiði'
        school.post_code = '260'
        school.municipality = 'Reykjanesbær'
        school.part = 'Suðurnes'
        school.save()
    else:
        print("school not found: Háaleitisskóli Reykjanesbæ")

    school = School.objects.filter(school_nr='1340', ssn='5704800149', name__startswith='Háaleitisskóli Reykjavík').first()
    if school:
        school.address = 'Álftamýri 79'
        school.post_code = '108'
        school.municipality = 'Reykjavíkurborg'
        school.part = 'Reykjavík'
        school.save()
    else:
        print("school not found: Háaleitisskóli Reykjavík")

    school = School.objects.filter(school_nr='1269', ssn='5302697609', name__startswith='Háteigsskóli').first()
    if school:
        school.address = 'v/Háteigsveg'
        school.post_code = '105'
        school.municipality = 'Reykjavíkurborg'
        school.part = 'Reykjavík'
        school.save()
    else:
        print("school not found: Háteigsskóli")

    school = School.objects.filter(school_nr='4121', ssn='6306061950', name__startswith='Heiðarskóli - Hvalfjarðarsveit').first()
    if school:
        school.address = 'Leirársveit'
        school.post_code = '301'
        school.municipality = 'Hvalfjarðarsveit'
        school.part = 'Vesturland'
        school.save()
    else:
        print("school not found: Heiðarskóli - Hvalfjarðarsveit")

    school = School.objects.filter(school_nr='3160', ssn='4909992809', name__startswith='Heiðarskóli - Reykjanesbæ').first()
    if school:
        school.address = 'Heiðarhvammi'
        school.post_code = '230'
        school.municipality = 'Reykjanesbær'
        school.part = 'Suðurnes'
        school.save()
    else:
        print("school not found: Heiðarskóli - Reykjanesbæ")

    school = School.objects.filter(school_nr='7234', ssn='4810872879', name__startswith='Hlíðarskóli').first()
    if school:
        school.address = 'Skjaldarvík'
        school.post_code = '601'
        school.municipality = 'Akureyrarkaupstaður'
        school.part = 'Norðurland eystra'
        school.save()
    else:
        print("school not found: Hlíðarskóli")

    school = School.objects.filter(school_nr='1247', ssn='5901821929', name__startswith='Hlíðaskóli').first()
    if school:
        school.address = 'Hamrahlíð 2'
        school.post_code = '105'
        school.municipality = 'Reykjavíkurborg'
        school.part = 'Reykjavík'
        school.save()
    else:
        print("school not found: Hlíðaskóli")

    school = School.objects.filter(school_nr='2263', ssn='6710883799', name__startswith='Hofsstaðaskóli').first()
    if school:
        school.address = 'v/Skólabraut'
        school.post_code = '210'
        school.municipality = 'Garðabær'
        school.part = 'Ngr. Reykjavíkur'
        school.save()
    else:
        print("school not found: Hofsstaðaskóli")

    school = School.objects.filter(school_nr='3159', ssn='5303840129', name__startswith='Holtaskóli').first()
    if school:
        school.address = 'Sunnubraut 32'
        school.post_code = '230'
        school.municipality = 'Reykjanesbær'
        school.part = 'Suðurnes'
        school.save()
    else:
        print("school not found: Holtaskóli")

    school = School.objects.filter(school_nr='1421', ssn='5901821769', name__startswith='Hólabrekkuskóli').first()
    if school:
        school.address = 'Suðurhólum 10'
        school.post_code = '111'
        school.municipality = 'Reykjavíkurborg'
        school.part = 'Reykjavík'
        school.save()
    else:
        print("school not found: Hólabrekkuskóli")

    school = School.objects.filter(school_nr='7321', ssn='5009740289', name__startswith='Hrafnagilsskóli').first()
    if school:
        school.address = 'Skólatröð 1'
        school.post_code = '601'
        school.municipality = 'Eyjafjarðarsveit'
        school.part = 'Norðurland eystra'
        school.save()
    else:
        print("school not found: Hrafnagilsskóli")

    school = School.objects.filter(school_nr='2183', ssn='5901697579', name__startswith='Hraunvallaskóli').first()
    if school:
        school.address = 'v/Ásvelli'
        school.post_code = '220'
        school.municipality = 'Hafnarfjarðarkaupstaður'
        school.part = 'Ngr. Reykjavíkur'
        school.save()
    else:
        print("school not found: Hraunvallaskóli")

    school = School.objects.filter(school_nr='6187', ssn='6705740169', name__startswith='Húnavallaskóli').first()
    if school:
        school.address = 'Húnavöllum'
        school.post_code = '541'
        school.municipality = 'Húnavatnshreppi'
        school.part = 'Norðurland vestra'
        school.save()
    else:
        print("school not found: Húnavallaskóli")

    school = School.objects.filter(school_nr='1462', ssn='6308911089', name__startswith='Húsaskóli').first()
    if school:
        school.address = 'Dalhúsum 41'
        school.post_code = '112'
        school.municipality = 'Reykjavíkurborg'
        school.part = 'Reykjavík'
        school.save()
    else:
        print("school not found: Húsaskóli")

    school = School.objects.filter(school_nr='2182', ssn='5708902049', name__startswith='Hvaleyrarskóli').first()
    if school:
        school.address = 'Akurholti 1'
        school.post_code = '220'
        school.municipality = 'Hafnarfjarðarkaupstaður'
        school.part = 'Ngr. Reykjavíkur'
        school.save()
    else:
        print("school not found: Hvaleyrarskóli")

    school = School.objects.filter(school_nr='9173', ssn='5201810249', name__startswith='Hvolsskóli').first()
    if school:
        school.address = 'Vallarbraut 16'
        school.post_code = '860'
        school.municipality = 'Rangárþing eystra'
        school.part = 'Suðurland'
        school.save()
    else:
        print("school not found: Hvolsskóli")

    school = School.objects.filter(school_nr='6221', ssn='6710888599', name__startswith='Höfðaskóli').first()
    if school:
        school.address = 'Bogabraut 2'
        school.post_code = '545'
        school.municipality = 'Sveitarf. Skagaströnd'
        school.part = 'Norðurland vestra'
        school.save()
    else:
        print("school not found: Höfðaskóli")

    school = School.objects.filter(school_nr='2395', ssn='4805061030', name__startswith='Hörðuvallaskóli').first()
    if school:
        school.address = 'Baugakór 38'
        school.post_code = '203'
        school.municipality = 'Kópavogsbær'
        school.part = 'Ngr. Reykjavíkur'
        school.save()
    else:
        print("school not found: Hörðuvallaskóli")

    school = School.objects.filter(school_nr='1478', ssn='4307012070', name__startswith='Ingunnarskóli').first()
    if school:
        school.address = 'Maríubaugi 1'
        school.post_code = '113'
        school.municipality = 'Reykjavíkurborg'
        school.part = 'Reykjavík'
        school.save()
    else:
        print("school not found: Ingunnarskóli")

    school = School.objects.filter(school_nr='2294', ssn='4309013030', name__startswith='Kársnesskóli').first()
    if school:
        school.address = 'v/Skólagerði'
        school.post_code = '200'
        school.municipality = 'Kópavogsbær'
        school.part = 'Ngr. Reykjavíkur'
        school.save()
    else:
        print("school not found: Kársnesskóli")

    school = School.objects.filter(school_nr='1481', ssn='5302697609', name__startswith='Kelduskóli').first()
    if school:
        school.address = 'Hamravík 10'
        school.post_code = '112'
        school.municipality = 'Reykjavíkurborg'
        school.part = 'Reykjavík'
        school.save()
    else:
        print("school not found: Kelduskóli")

    school = School.objects.filter(school_nr='9419', ssn='5906982109', name__startswith='Kerhólsskóli').first()
    if school:
        school.address = 'Borg'
        school.post_code = '801'
        school.municipality = 'Grímsnes- og Grafningshreppur'
        school.part = 'Suðurland'
        school.save()
    else:
        print("school not found: Kerhólsskóli")

    school = School.objects.filter(school_nr='9117', ssn='4806902069', name__startswith='Kirkjubæjarskóli').first()
    if school:
        school.address = 'Klausturvegi 4'
        school.post_code = '880'
        school.municipality = 'Skaftárhreppur'
        school.part = 'Suðurland'
        school.save()
    else:
        print("school not found: Kirkjubæjarskóli")

    school = School.objects.filter(school_nr='1998', ssn='5302697609', name__startswith='Klettaskóli').first()
    if school:
        school.address = 'Suðurhlíð 9'
        school.post_code = '105'
        school.municipality = 'Reykjavíkurborg'
        school.part = 'Reykjavík'
        school.save()
    else:
        print("school not found: Klettaskóli")

    school = School.objects.filter(school_nr='1484', ssn='6710885069', name__startswith='Klébergsskóli').first()
    if school:
        school.address = 'Kjalarnesi'
        school.post_code = '116'
        school.municipality = 'Reykjavíkurborg'
        school.part = 'Reykjavík'
        school.save()
    else:
        print("school not found: Klébergsskóli")

    school = School.objects.filter(school_nr='2323', ssn='6710883289', name__startswith='Kópavogsskóli').first()
    if school:
        school.address = 'v/Digranesveg'
        school.post_code = '200'
        school.municipality = 'Kópavogsbær'
        school.part = 'Ngr. Reykjavíkur'
        school.save()
    else:
        print("school not found: Kópavogsskóli")

    school = School.objects.filter(school_nr='2435', ssn='4702695969', name__startswith='Krikaskóli').first()
    if school:
        school.address = 'Sunnukrika 1'
        school.post_code = '270'
        school.municipality = 'Mosfellsbær'
        school.part = 'Ngr. Reykjavíkur'
        school.save()
    else:
        print("school not found: Krikaskóli")

    school = School.objects.filter(school_nr='1157', ssn='6101710369', name__startswith='Landakotsskóli').first()
    if school:
        school.address = 'Túngötu 15'
        school.post_code = '101'
        school.municipality = 'Reykjavíkurborg'
        school.part = 'Reykjavík'
        school.save()
    else:
        print("school not found: Landakotsskóli")

    school = School.objects.filter(school_nr='1322', ssn='5901823709', name__startswith='Langholtsskóli').first()
    if school:
        school.address = 'Holtavegi 23'
        school.post_code = '104'
        school.municipality = 'Reykjavíkurborg'
        school.part = 'Reykjavík'
        school.save()
    else:
        print("school not found: Langholtsskóli")

    school = School.objects.filter(school_nr='9227', ssn='5201750169', name__startswith='Laugalandsskóli í Holtum').first()
    if school:
        school.address = 'Holtum'
        school.post_code = '851'
        school.municipality = 'Rangárþingi ytra'
        school.part = 'Suðurland'
        school.save()
    else:
        print("school not found: Laugalandsskóli í Holtum")

    school = School.objects.filter(school_nr='1292', ssn='5901823979', name__startswith='Laugalækjarskóli').first()
    if school:
        school.address = 'Leirulækur 2'
        school.post_code = '105'
        school.municipality = 'Reykjavíkurborg'
        school.part = 'Reykjavík'
        school.save()
    else:
        print("school not found: Laugalækjarskóli")

    school = School.objects.filter(school_nr='4231', ssn='6908942469', name__startswith='Laugargerðisskóli').first()
    if school:
        school.address = 'Snæfellsnesi'
        school.post_code = '311'
        school.municipality = 'Eyja-og Miklaholtshreppur'
        school.part = 'Vesturland'
        school.save()
    else:
        print("school not found: Laugargerðisskóli")

    school = School.objects.filter(school_nr='1281', ssn='5302697609', name__startswith='Laugarnesskóli').first()
    if school:
        school.address = 'Kirkjuteigi 24'
        school.post_code = '105'
        school.municipality = 'Reykjavíkurborg'
        school.part = 'Reykjavík'
        school.save()
    else:
        print("school not found: Laugarnesskóli")

    school = School.objects.filter(school_nr='2437', ssn='4702695969', name__startswith='Lágafellsskóli').first()
    if school:
        school.address = 'v/Lækjarhlíð'
        school.post_code = '270'
        school.municipality = 'Mosfellsbær'
        school.part = 'Ngr. Reykjavíkur'
        school.save()
    else:
        print("school not found: Lágafellsskóli")

    school = School.objects.filter(school_nr='2390', ssn='6006972939', name__startswith='Lindaskóli').first()
    if school:
        school.address = 'Núpalind 7'
        school.post_code = '201'
        school.municipality = 'Kópavogsbær'
        school.part = 'Ngr. Reykjavíkur'
        school.save()
    else:
        print("school not found: Lindaskóli")

    school = School.objects.filter(school_nr='7291', ssn='6710889489', name__startswith='Lundarskóli').first()
    if school:
        school.address = 'v/Dalsbraut'
        school.post_code = '600'
        school.municipality = 'Akureyrarkaupstaður'
        school.part = 'Norðurland eystra'
        school.save()
    else:
        print("school not found: Lundarskóli")

    school = School.objects.filter(school_nr='2213', ssn='6710884099', name__startswith='Lækjarskóli').first()
    if school:
        school.address = 'Sólvangsvegi 4'
        school.post_code = '220'
        school.municipality = 'Hafnarfjarðarkaupstaður'
        school.part = 'Ngr. Reykjavíkur'
        school.save()
    else:
        print("school not found: Lækjarskóli")

    school = School.objects.filter(school_nr='1123', ssn='5901824279', name__startswith='Melaskóli').first()
    if school:
        school.address = 'Hagamel 1'
        school.post_code = '107'
        school.municipality = 'Reykjavíkurborg'
        school.part = 'Reykjavík'
        school.save()
    else:
        print("school not found: Melaskóli")

    school = School.objects.filter(school_nr='3148', ssn='6710884339', name__startswith='Myllubakkaskóli').first()
    if school:
        school.address = 'Sólvallagötu 6a'
        school.post_code = '230'
        school.municipality = 'Reykjanesbær'
        school.part = 'Suðurnes'
        school.save()
    else:
        print("school not found: Myllubakkaskóli")

    school = School.objects.filter(school_nr='7295', ssn='5301090110', name__startswith='Naustaskóli').first()
    if school:
        school.address = 'Hólmatúni 2'
        school.post_code = '600'
        school.municipality = 'Akureyrarkaupstaður'
        school.part = 'Norðurland eystra'
        school.save()
    else:
        print("school not found: Naustaskóli")

    school = School.objects.filter(school_nr='8296', ssn='6810885049', name__startswith='Nesskóli').first()
    if school:
        school.address = 'Skólavegi 9'
        school.post_code = '740'
        school.municipality = 'Fjarðabyggð'
        school.part = 'Austurland'
        school.save()
    else:
        print("school not found: Nesskóli")

    school = School.objects.filter(school_nr='3167', ssn='6710884689', name__startswith='Njarðvíkurskóli').first()
    if school:
        school.address = 'Brekkustíg 2'
        school.post_code = '260'
        school.municipality = 'Reykjanesbær'
        school.part = 'Suðurnes'
        school.save()
    else:
        print("school not found: Njarðvíkurskóli")

    school = School.objects.filter(school_nr='1435', ssn='5305051380', name__startswith='Norðlingaskóli').first()
    if school:
        school.address = 'Árvaði 3'
        school.post_code = '110'
        school.municipality = 'Reykjavíkurborg'
        school.part = 'Reykjavík'
        school.save()
    else:
        print("school not found: Norðlingaskóli")

    school = School.objects.filter(school_nr='7271', ssn='4911872639', name__startswith='Oddeyrarskóli').first()
    if school:
        school.address = 'v/Víðivelli'
        school.post_code = '600'
        school.municipality = 'Akureyrarkaupstaður'
        school.part = 'Norðurland eystra'
        school.save()
    else:
        print("school not found: Oddeyrarskóli")

    school = School.objects.filter(school_nr='5118', ssn='4407872589', name__startswith='Reykhólaskóli').first()
    if school:
        school.address = 'Skólabraut 1'
        school.post_code = '380'
        school.municipality = 'Reykhólahreppur'
        school.part = 'Vestfirðir'
        school.save()
    else:
        print("school not found: Reykhólaskóli")

    school = School.objects.filter(school_nr='7383', ssn='4401691399', name__startswith='Reykjahlíðarskóli').first()
    if school:
        school.address = 'Hlíðavegi 6'
        school.post_code = '660'
        school.municipality = 'Skútustaðahreppur'
        school.part = 'Norðurland eystra'
        school.save()
    else:
        print("school not found: Reykjahlíðarskóli")

    school = School.objects.filter(school_nr='1458', ssn='6103140900', name__startswith='Reykjavík International School').first()
    if school:
        school.address = 'Dyrhömrum 9'
        school.post_code = '112'
        school.municipality = 'Reykjavíkurborg'
        school.part = 'Reykjavík'
        school.save()
    else:
        print("school not found: Reykjavík International School")

    school = School.objects.filter(school_nr='1367', ssn='5901823549', name__startswith='Réttarholtsskóli').first()
    if school:
        school.address = 'v/Réttarholtsveg'
        school.post_code = '108'
        school.municipality = 'Reykjavíkurborg'
        school.part = 'Reykjavík'
        school.save()
    else:
        print("school not found: Réttarholtsskóli")

    school = School.objects.filter(school_nr='1466', ssn='6206932789', name__startswith='Rimaskóli').first()
    if school:
        school.address = 'Rósarima 11'
        school.post_code = '112'
        school.municipality = 'Reykjavíkurborg'
        school.part = 'Reykjavík'
        school.save()
    else:
        print("school not found: Rimaskóli")

    school = School.objects.filter(school_nr='2392', ssn='6706013070', name__startswith='Salaskóli').first()
    if school:
        school.address = 'Versölum 5'
        school.post_code = '201'
        school.municipality = 'Kópavogsbær'
        school.part = 'Ngr. Reykjavíkur'
        school.save()
    else:
        print("school not found: Salaskóli")

    school = School.objects.filter(school_nr='1432', ssn='4506861239', name__startswith='Selásskóli').first()
    if school:
        school.address = 'Selásbraut'
        school.post_code = '110'
        school.municipality = 'Reykjavíkurborg'
        school.part = 'Reykjavík'
        school.save()
    else:
        print("school not found: Selásskóli")

    school = School.objects.filter(school_nr='1382', ssn='5901823629', name__startswith='Seljaskóli').first()
    if school:
        school.address = 'Kleifarseli 28'
        school.post_code = '109'
        school.municipality = 'Reykjavíkurborg'
        school.part = 'Reykjavík'
        school.save()
    else:
        print("school not found: Seljaskóli")

    school = School.objects.filter(school_nr='2222', ssn='5701902619', name__startswith='Setbergsskóli').first()
    if school:
        school.address = 'v/Hlíðarberg'
        school.post_code = '220'
        school.municipality = 'Hafnarfjarðarkaupstaður'
        school.part = 'Ngr. Reykjavíkur'
        school.save()
    else:
        print("school not found: Setbergsskóli")

    school = School.objects.filter(school_nr='8251', ssn='6810884909', name__startswith='Seyðisfjarðarskóli').first()
    if school:
        school.address = 'Suðurgötu 4'
        school.post_code = '710'
        school.municipality = 'Seyðisfjarðarkaupstaður'
        school.part = 'Austurland'
        school.save()
    else:
        print("school not found: Seyðisfjarðarskóli")

    school = School.objects.filter(school_nr='7223', ssn='6710889569', name__startswith='Síðuskóli').first()
    if school:
        school.address = 'v/Bugðusíðu'
        school.post_code = '603'
        school.municipality = 'Akureyrarkaupstaður'
        school.part = 'Norðurland eystra'
        school.save()
    else:
        print("school not found: Síðuskóli")

    school = School.objects.filter(school_nr='2248', ssn='6908052420', name__startswith='Sjálandsskóli').first()
    if school:
        school.address = 'Löngulínu 8'
        school.post_code = '210'
        school.municipality = 'Garðabær'
        school.part = 'Ngr. Reykjavíkur'
        school.save()
    else:
        print("school not found: Sjálandsskóli")

    school = School.objects.filter(school_nr='1249', ssn='6002694889', name__startswith='Skóli Ísaks Jónssonar').first()
    if school:
        school.address = 'Bólstaðarhlíð 20'
        school.post_code = '105'
        school.municipality = 'Reykjavíkurborg'
        school.part = 'Reykjavík'
        school.save()
    else:
        print("school not found: Skóli Ísaks Jónssonar")

    school = School.objects.filter(school_nr='2312', ssn='4807942739', name__startswith='Smáraskóli').first()
    if school:
        school.address = 'Dalsmára 1'
        school.post_code = '201'
        school.municipality = 'Kópavogsbær'
        school.part = 'Ngr. Reykjavíkur'
        school.save()
    else:
        print("school not found: Smáraskóli")

    school = School.objects.filter(school_nr='2373', ssn='6710883369', name__startswith='Snælandsskóli').first()
    if school:
        school.address = 'Víðigrund'
        school.post_code = '200'
        school.municipality = 'Kópavogsbær'
        school.part = 'Ngr. Reykjavíkur'
        school.save()
    else:
        print("school not found: Snælandsskóli")

    school = School.objects.filter(school_nr='7361', ssn='7005730289', name__startswith='Stórutjarnaskóli').first()
    if school:
        school.address = 'Ljósavatnsskarði'
        school.post_code = '641'
        school.municipality = 'Þingeyjarsveit'
        school.part = 'Norðurland eystra'
        school.save()
    else:
        print("school not found: Stórutjarnaskóli")

    school = School.objects.filter(school_nr='3178', ssn='6710885499', name__startswith='Stóru-Vogaskóli').first()
    if school:
        school.address = 'Vogum, Vatnsleysustrandahreppi'
        school.post_code = '190'
        school.municipality = 'Sveitarfélagið Vogar'
        school.part = 'Suðurnes'
        school.save()
    else:
        print("school not found: Stóru-Vogaskóli")

    school = School.objects.filter(school_nr='8368', ssn='6810886449', name__startswith='Stöðvarfjarðarskóli').first()
    if school:
        school.address = 'Skólabraut 20'
        school.post_code = '755'
        school.municipality = 'Fjarðabyggð'
        school.part = 'Austurland'
        school.save()
    else:
        print("school not found: Stöðvarfjarðarskóli")

    school = School.objects.filter(school_nr='1224', ssn='4401693259', name__startswith='Suðurhlíðarskóli').first()
    if school:
        school.address = 'Suðurhlíð 36'
        school.post_code = '105'
        school.municipality = 'Reykjavíkurborg'
        school.part = 'Reykjavík'
        school.save()
    else:
        print("school not found: Suðurhlíðarskóli")

    school = School.objects.filter(school_nr='9312', ssn='5509042330', name__startswith='Sunnulækjarskóli').first()
    if school:
        school.address = 'Norðurhólum 1'
        school.post_code = '800'
        school.municipality = 'Sveitarfélagið Árborg'
        school.part = 'Suðurland'
        school.save()
    else:
        print("school not found: Sunnulækjarskóli")

    school = School.objects.filter(school_nr='5319', ssn='5606861379', name__startswith='Súðavíkurskóli').first()
    if school:
        school.address = 'v/Grundarstræti'
        school.post_code = '420'
        school.municipality = 'Súðavikurhreppur'
        school.part = 'Vestfirðir'
        school.save()
    else:
        print("school not found: Súðavíkurskóli")

    school = School.objects.filter(school_nr='1476', ssn='5302697609', name__startswith='Sæmundarskóli').first()
    if school:
        school.address = 'Gvendargeisla 168'
        school.post_code = '113'
        school.municipality = 'Reykjavíkurborg'
        school.part = 'Reykjavík'
        school.save()
    else:
        print("school not found: Sæmundarskóli")

    school = School.objects.filter(school_nr='1189', ssn='4601881999', name__startswith='Tjarnarskóli').first()
    if school:
        school.address = 'Lækjargötu 14b'
        school.post_code = '101'
        school.municipality = 'Reykjavíkurborg'
        school.part = 'Reykjavík'
        school.save()
    else:
        print("school not found: Tjarnarskóli")

    school = School.objects.filter(school_nr='9310', ssn='6810887769', name__startswith='Vallaskóli').first()
    if school:
        school.address = 'v/Bankaveg'
        school.post_code = '800'
        school.municipality = 'Sveitarfélagið Árborg'
        school.part = 'Suðurland'
        school.save()
    else:
        print("school not found: Vallaskóli")

    school = School.objects.filter(school_nr='7358', ssn='6810883939', name__startswith='Valsárskóli').first()
    if school:
        school.address = 'Svalbarðsströnd'
        school.post_code = '601'
        school.municipality = 'Svalbarðsstrandarhreppur'
        school.part = 'Norðurland eystra'
        school.save()
    else:
        print("school not found: Valsárskóli")

    school = School.objects.filter(school_nr='6299', ssn='4612730179', name__startswith='Varmahlíðarskóli').first()
    if school:
        school.address = 'Varmahlíð'
        school.post_code = '560'
        school.municipality = 'Sveitarf. Skagafjörður'
        school.part = 'Norðurland vestra'
        school.save()
    else:
        print("school not found: Varmahlíðarskóli")

    school = School.objects.filter(school_nr='2439', ssn='6710884849', name__startswith='Varmárskóli').first()
    if school:
        school.address = 'v/Skólabraut'
        school.post_code = '270'
        school.municipality = 'Mosfellsbær'
        school.part = 'Ngr. Reykjavíkur'
        school.save()
    else:
        print("school not found: Varmárskóli")

    school = School.objects.filter(school_nr='2393', ssn='5808051080', name__startswith='Vatnsendaskóli').first()
    if school:
        school.address = 'v/Funahvarf'
        school.post_code = '203'
        school.municipality = 'Kópavogsbær'
        school.part = 'Ngr. Reykjavíkur'
        school.save()
    else:
        print("school not found: Vatnsendaskóli")

    school = School.objects.filter(school_nr='1146', ssn='5302697609', name__startswith='Vesturbæjarskóli').first()
    if school:
        school.address = 'Sólvallagötu 67'
        school.post_code = '101'
        school.municipality = 'Reykjavíkurborg'
        school.part = 'Reykjavík'
        school.save()
    else:
        print("school not found: Vesturbæjarskóli")

    school = School.objects.filter(school_nr='2233', ssn='6710884179', name__startswith='Víðistaðaskóli').first()
    if school:
        school.address = 'Hrauntungu 7'
        school.post_code = '220'
        school.municipality = 'Hafnarfjarðarkaupstaður'
        school.part = 'Ngr. Reykjavíkur'
        school.save()
    else:
        print("school not found: Víðistaðaskóli")

    school = School.objects.filter(school_nr='9122', ssn='4612830399', name__startswith='Víkurskóli').first()
    if school:
        school.address = 'Mánabraut 5-7'
        school.post_code = '870'
        school.municipality = 'Mýrdalshreppur'
        school.part = 'Suðurland'
        school.save()
    else:
        print("school not found: Víkurskóli")

    school = School.objects.filter(school_nr='1333', ssn='5901823119', name__startswith='Vogaskóli').first()
    if school:
        school.address = 'v/Skeiðarvog'
        school.post_code = '104'
        school.municipality = 'Reykjavíkurborg'
        school.part = 'Reykjavík'
        school.save()
    else:
        print("school not found: Vogaskóli")

    school = School.objects.filter(school_nr='8127', ssn='6810885479', name__startswith='Vopnafjarðarskóli').first()
    if school:
        school.address = 'Lónabraut 12'
        school.post_code = '690'
        school.municipality = 'Vopnafjarðarhreppur'
        school.part = 'Austurland'
        school.save()
    else:
        print("school not found: Vopnafjarðarskóli")

    school = School.objects.filter(school_nr='1470', ssn='5302697609', name__startswith='Vættaskóli').first()
    if school:
        school.address = 'Vættaborgum 9'
        school.post_code = '112'
        school.municipality = 'Reykjavíkurborg'
        school.part = 'Reykjavík'
        school.save()
    else:
        print("school not found: Vættaskóli")

    school = School.objects.filter(school_nr='1470', ssn='5302697609', name__startswith='Vættaskóli').first()
    if school:
        school.address = 'Vallengi 14'
        school.post_code = '113'
        school.municipality = 'Reykjavíkurborg'
        school.part = 'Reykjavík'
        school.save()
    else:
        print("school not found: Vættaskóli")

    school = School.objects.filter(school_nr='2396', ssn='6107972029', name__startswith='Waldorfskólinn í Lækjarbotnum').first()
    if school:
        school.address = 'Lækjarbotnaland 53'
        school.post_code = '203'
        school.municipality = 'Kópavogsbær'
        school.part = 'Ngr. Reykjavíkur'
        school.save()
    else:
        print("school not found: Waldorfskólinn í Lækjarbotnum")

    school = School.objects.filter(school_nr='1425', ssn='4306942199', name__startswith='Waldorfskólinn Sólstafir').first()
    if school:
        school.address = 'Sóltúni 6'
        school.post_code = '111'
        school.municipality = 'Reykjavíkurborg'
        school.part = 'Reykjavík'
        school.save()
    else:
        print("school not found: Waldorfskólinn Sólstafir")

    school = School.objects.filter(school_nr='7192', ssn='5909740649', name__startswith='Þelamerkurskóli').first()
    if school:
        school.address = ''
        school.post_code = '601'
        school.municipality = 'Hörgársveit'
        school.part = 'Norðurland eystra'
        school.save()
    else:
        print("school not found: Þelamerkurskóli")

    school = School.objects.filter(school_nr='7433', ssn='6407120900', name__startswith='Þingeyjarskóli').first()
    if school:
        school.address = 'Laugar/Hafralæk'
        school.post_code = '650'
        school.municipality = 'Þingeyjarsveit'
        school.part = 'Norðurland eystra'
        school.save()
    else:
        print("school not found: Þingeyjarskóli")

    school = School.objects.filter(school_nr='9341', ssn='5406024410', name__startswith='Þjórsárskóli').first()
    if school:
        school.address = 'Árnes'
        school.post_code = '801'
        school.municipality = 'Skeiða- og Gnúpverjahreppi'
        school.part = 'Suðurland'
        school.save()
    else:
        print("school not found: Þjórsárskóli")

    school = School.objects.filter(school_nr='1393', ssn='5901823469', name__startswith='Ölduselsskóli').first()
    if school:
        school.address = 'Ölduseli 17'
        school.post_code = '109'
        school.municipality = 'Reykjavíkurborg'
        school.part = 'Reykjavík'
        school.save()
    else:
        print("school not found: Ölduselsskóli")

    school = School.objects.filter(school_nr='2193', ssn='6809872549', name__startswith='Öldutúnsskóli').first()
    if school:
        school.address = 'Öldutúni'
        school.post_code = '220'
        school.municipality = 'Hafnarfjarðarkaupstaður'
        school.part = 'Ngr. Reykjavíkur'
        school.save()
    else:
        print("school not found: Öldutúnsskóli")

