from django.shortcuts import render

from common.models import *
from .models       import *

from django.shortcuts           import render, render_to_response, get_object_or_404, redirect
from django.contrib.auth.mixins import UserPassesTestMixin
from django.views.generic       import ListView, CreateView, DetailView, UpdateView, DeleteView
from django.core.urlresolvers   import reverse_lazy, reverse
from django.http                import HttpResponse

import csv
import xlrd
import openpyxl
from itertools        import chain
from django.db.models import Count


from schools.util import *
from .util        import *


def excel_result(request, school_id, year, group):
	school   = School.objects.get(id=school_id)
	response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
	response['Content-Disposition'] = 'attachment; filename='+school.name+'-'+year+'-'+group+'-bekkur.xlsx'
	wb       = openpyxl.Workbook()
	ws       = wb.get_active_sheet()
	ws.title = "Íslenska"

	ws['A1']=  'Nemandi'
	ws['B1']=  'Kennitala'
	ws['C1']=  'Samræmd-Lestur'
	ws['D1']=  'Samræmd-Málnotkun'
	ws['E1']=  'Samræmd-Ritun'
	ws['F1']=  'Samræmd-Heild'
	ws['G1']=  'Raðeinkunn-Lestur'
	ws['H1']=  'Raðeinkunn-Málnotkun'
	ws['I1']=  'Raðeinkunn-Ritun'
	ws['J1']=  'Raðeinkunn-Heild'
	ws['K1']=  'Grunnskólaeinkunn-Lestur'
	ws['L1']=  'Grunnskólaeinkunn-Málnotkun'
	ws['M1']=  'Grunnskólaeinkunn-Ritun'
	ws['N1']=  'Grunnskólaeinkunn-Heild'
	ws['O1']=  'Framfaraflokkur'
	ws['P1']=  'Framfaratexti'
	#prepare data
	results = SamraemdISLResult.objects.filter(student__in = Student.objects.filter(school=school)).filter(student_year=group).filter(exam_date__year=year)

	index = 2
	for result in results:
		ws.cell('A'+str(index)).value = result.student.name
		ws.cell('B'+str(index)).value = result.student.ssn
		ws.cell('C'+str(index)).value = result.le_se.replace('.',',')
		ws.cell('D'+str(index)).value = result.mn_se.replace('.',',')
		ws.cell('E'+str(index)).value = result.ri_se.replace('.',',')
		ws.cell('F'+str(index)).value = result.se.replace('.',',')
		ws.cell('G'+str(index)).value = result.le_re.replace('.',',')
		ws.cell('H'+str(index)).value = result.mn_re.replace('.',',')
		ws.cell('I'+str(index)).value = result.ri_re.replace('.',',')
		ws.cell('J'+str(index)).value = result.re.replace('.',',')
		ws.cell('K'+str(index)).value = result.le_sg.replace('.',',')
		ws.cell('L'+str(index)).value = result.mn_sg.replace('.',',')
		ws.cell('M'+str(index)).value = result.ri_sg
		ws.cell('N'+str(index)).value = result.sg
		ws.cell('O'+str(index)).value = result.fm_fl.replace('.0','')
		ws.cell('P'+str(index)).value = result.fm_txt
		index+=1
	ws = wb.create_sheet(title='Stærðfræði')

	ws['A1']=  'Nemandi'
	ws['B1']=  'Kennitala'
	ws['C1']=  'Samræmd-Reikningur og aðgerðir'
	ws['D1']=  'Samræmd-Rúmfræði og mælingar'
	ws['E1']=  'Samræmd-Tölur og talnaskilningur'
	ws['F1']=  'Samræmd-Heild'
	ws['G1']=  'Raðeinkunn-Reikningur og aðgerðir'
	ws['H1']=  'Raðeinkunn-Rúmfræði og mælingar'
	ws['I1']=  'Raðeinkunn-Tölur og talnaskilningur'
	ws['J1']=  'Raðeinkunn-Heild'
	ws['K1']=  'Grunnskólaeinkunn-Reikningur og aðgerðir'
	ws['L1']=  'Grunnskólaeinkunn-Rúmfræði og mælingar'
	ws['M1']=  'Grunnskólaeinkunn-Tölur og talnaskilningur'
	ws['N1']=  'Grunnskólaeinkunn-Heild'
	ws['O1']=  'Framfaraflokkur'
	ws['P1']=  'Framfaratexti'
	ws['Q1']=  'Orðadæmi og talnadæmi'
	#prepare data
	results = SamraemdMathResult.objects.filter(student__in = Student.objects.filter(school=school)).filter(student_year=group).filter(exam_date__year=year)

	index = 2
	for result in results:
		ws.cell('A'+str(index)).value = result.student.name
		ws.cell('B'+str(index)).value = result.student.ssn
		ws.cell('C'+str(index)).value = result.ra_se.replace('.',',')
		ws.cell('D'+str(index)).value = result.rm_se.replace('.',',')
		ws.cell('E'+str(index)).value = result.tt_se.replace('.',',')
		ws.cell('F'+str(index)).value = result.se
		ws.cell('G'+str(index)).value = result.ra_re
		ws.cell('H'+str(index)).value = result.rm_re
		ws.cell('I'+str(index)).value = result.tt_re
		ws.cell('J'+str(index)).value = result.re
		ws.cell('K'+str(index)).value = result.ra_sg
		ws.cell('L'+str(index)).value = result.rm_sg
		ws.cell('M'+str(index)).value = result.tt_sg
		ws.cell('N'+str(index)).value = result.sg
		ws.cell('O'+str(index)).value = result.fm_fl.replace('.0','')
		ws.cell('P'+str(index)).value = result.fm_txt
		ws.cell('Q'+str(index)).value = result.ord_talna_txt
		index+=1

	wb.save(response)

	return response

class SamraemdResultDetail(UserPassesTestMixin, DetailView):
	model = SamraemdMathResult

	def test_func(self):
		return is_school_manager(self.request, self.kwargs)

	def get_template_names(self, **kwargs):
		return ['samraemd/samraemdresult_detail.html']

	def get_object(self, **kwargs):
		return SamraemdMathResult.objects.first()

	def get_context_data(self, **kwargs):
		context         = super(SamraemdResultDetail, self).get_context_data(**kwargs)
		year            = self.kwargs['year']
		group           = self.kwargs['group']
		student_results = {}
		if 'school_id' in self.kwargs:
			school               = School.objects.get(pk=self.kwargs['school_id'])
			context['school']    = school
			context['school_id'] = self.kwargs['school_id']
			for result in list(chain(
				SamraemdMathResult.objects.filter(student__in = Student.objects.filter(school=school)).filter(student_year=group).filter(exam_date__year=year),
				SamraemdISLResult.objects.filter(student__in = Student.objects.filter(school=school)).filter(student_year=group).filter(exam_date__year=year),
				)):
				if result.student in student_results:
					student_results[result.student].append(result)
				else:
					student_results[result.student] = [result]
		else:
			if self.request.user.is_superuser:
				if 'stæ' in self.request.path:
					for result in SamraemdMathResult.objects.filter(student_year=group).filter(exam_date__year=year):
						if result.student in student_results:
							student_results[result.student].append(result)
						else:
							student_results[result.student] = [result]
				else:
					for result in SamraemdISLResult.objects.filter(student_year=group).filter(exam_date__year=year):
						if result.student in student_results:
							student_results[result.student].append(result)
						else:
							student_results[result.student] = [result]			
		context['student_results'] = student_results
		return context

class SamraemdMathResultAdminListing(UserPassesTestMixin, ListView):
	model = SamraemdMathResult
	template_name = 'samraemd/samraemdresult_admin_list.html'

	def get_context_data(self, **kwargs):
		# xxx will be available in the template as the related objects
		context              = super(SamraemdMathResultAdminListing, self).get_context_data(**kwargs)
		context['exams']     = SamraemdMathResult.objects.all().values('exam_date', 'student_year', 'exam_code').distinct()
		context['raw_exams'] = SamraemdResult.objects.filter(exam_code=3).values('exam_date', 'student_year', 'exam_name', 'exam_code').distinct()
		return context

	def test_func(self):
		return self.request.user.is_superuser

class SamraemdMathResultListing(UserPassesTestMixin, ListView):
	model = SamraemdMathResult

	def get_context_data(self, **kwargs):
		# xxx will be available in the template as the related objects
		context              = super(SamraemdMathResultListing, self).get_context_data(**kwargs)
		school               = School.objects.get(pk=self.kwargs['school_id'])
		context['exams']     = SamraemdMathResult.objects.filter(student__in = Student.objects.filter(school=school)).values('exam_code').distinct()
		context['school_id'] = school.id
		return context

	def test_func(self):
		return is_school_manager(self.request, self.kwargs) or is_school_teacher(self.request, self.kwargs)

class SamraemdResultListing(UserPassesTestMixin, ListView):
	model = SamraemdMathResult
	template_name = 'samraemd/samraemdschoolresult_list.html'

	def get_context_data(self, **kwargs):
		# xxx will be available in the template as the related objects
		context              = super(SamraemdResultListing, self).get_context_data(**kwargs)
		school               = School.objects.get(pk=self.kwargs['school_id'])
		context['school']    = school
		m_exams              = SamraemdMathResult.objects.filter(student__in = Student.objects.filter(school=school)).values('exam_date', 'student_year', 'exam_code').distinct()
		i_exams              = SamraemdISLResult.objects.filter(student__in = Student.objects.filter(school=school)).values('exam_date', 'student_year', 'exam_code').distinct()
		exams                = SamraemdResult.objects.filter(student__in = Student.objects.filter(school=school),exam_code=3).values('exam_date', 'student_year', 'exam_code', 'exam_name').distinct()
		context['exams']     = list(chain(m_exams, i_exams))
		context['links']     = m_exams
		context['rawlinks']  = exams
		context['school_id'] = school.id
		return context

	def test_func(self):
		return is_school_manager(self.request, self.kwargs) or is_school_teacher(self.request, self.kwargs)

class SamraemdResultDetail(UserPassesTestMixin, DetailView):
	model = SamraemdMathResult

	def test_func(self):
		return is_school_manager(self.request, self.kwargs)

	def get_template_names(self, **kwargs):
		if 'einkunnablod' in self.request.path:
			return ['samraemd/samraemd_detail_print_singles.html']
		return ['samraemd/samraemdresult_detail.html']

	def get_object(self, **kwargs):
		return SamraemdMathResult.objects.first()

	def get_context_data(self, **kwargs):
		# xxx will be available in the template as the related objects
		context = super(SamraemdResultDetail, self).get_context_data(**kwargs)
		year = self.kwargs['year']
		context['year'] = year
		group = self.kwargs['group']
		context['group'] = group
		student_results = {}
		if 'school_id' in self.kwargs:
			school = School.objects.get(pk=self.kwargs['school_id'])
			context['school'] = school
			context['school_id'] = self.kwargs['school_id']
			context['school_name'] = school.name
			for result in list(chain(
				SamraemdISLResult.objects.filter(student__in = Student.objects.filter(school=school)).filter(student_year=group).filter(exam_date__year=year),
				SamraemdMathResult.objects.filter(student__in = Student.objects.filter(school=school)).filter(student_year=group).filter(exam_date__year=year),
				)):
				if result.student in student_results:
					student_results[result.student].append(result)
				else:
					student_results[result.student] = [result]
		else:
			if self.request.user.is_superuser:
				if 'stæ' in self.request.path:
					for result in SamraemdMathResult.objects.filter(student_year=group).filter(exam_date__year=year):
						if result.student in student_results:
							student_results[result.student].append(result)
						else:
							student_results[result.student] = [result]
				elif 'isl' in self.request.path:
					for result in SamraemdISLResult.objects.filter(student_year=group).filter(exam_date__year=year):
						if result.student in student_results:
							student_results[result.student].append(result)
						else:
							student_results[result.student] = [result]
		context['student_results'] = student_results

		return context

class SamraemdMathResultCreate(UserPassesTestMixin, CreateView):
	model = SamraemdMathResult
	form_class = SamraemdMathResultForm	
	template_name = "samraemd/form_import.html"
	login_url = reverse_lazy('denied')

	def post(self, *args, **kwargs):
		if(self.request.FILES):
			u_file = self.request.FILES['file'].name
			extension = u_file.split(".")[-1]
			exam_code = self.request.POST.get('exam_code').strip()
			exam_date = self.request.POST.get('exam_date').strip()
			student_year = self.request.POST.get('student_year').strip()

			try:
				student_ssn=ra_se=rm_se=tt_se=se=ra_re=rm_re=tt_re=re=ra_sg=rm_sg=tt_sg=sg=fm_fl=fm_txt=ord_talna_txt=''
				if extension.lower() == 'csv':
					for row in self.request.FILES['file'].readlines()[1:]:
						row = row.decode('utf-8')
						row = row.replace('"', '')
						row_data = row.split(',')
						student = Student.objects.filter(ssn=row_data[0].strip()) #student already exists
						if student:
							#check if results for student exists, create if not, otherwise update
							results = SamraemdMathResult.objects.filter(student=student, exam_code=exam_code)
							results_dict = {
								'student'      : student.first(),
								'ra_se'        : row_data[1].strip(),
								'rm_se'        : row_data[2].strip(),
								'tt_se'        : row_data[3].strip(),
								'se'           : row_data[4].strip(),
								'ra_re'        : row_data[5].strip(),
								'rm_re'        : row_data[6].strip(),
								'tt_re'        : row_data[7].strip(),
								're'           : row_data[8].strip(),
								'ra_sg'        : row_data[9].strip(),
								'rm_sg'        : row_data[10].strip(),
								'tt_sg'        : row_data[11].strip(),
								'sg'           : row_data[12].strip(),
								'fm_fl'        : row_data[13].strip(),
								'fm_txt'       : row_data[14].strip(),
								'ord_talna_txt': row_data[15].strip(),
								'exam_code'    : exam_code,
								'exam_date'    : exam_date,
								'student_year' : student_year
							}
							if results:
								results.update(**results_dict)
							else:
								results = SamraemdMathResult.objects.create(**results_dict)
				elif extension == 'xlsx':
					input_excel = self.request.FILES['file']
					book = xlrd.open_workbook(file_contents=input_excel.read())
					for sheetsnumber in range(book.nsheets):
						sheet = book.sheet_by_index(sheetsnumber)
						for row in range(1, sheet.nrows):
							student = Student.objects.filter(ssn=str(sheet.cell_value(row,0)).strip()) #student already exists
							if student:
								#check if results for student exists, create if not, otherwise update
								results = SamraemdMathResult.objects.filter(student=student, exam_code=exam_code)
								results_dict = {
									'student'      : student.first(),
									'ra_se'        : str(sheet.cell_value(row,1)).strip(),
									'rm_se'        : str(sheet.cell_value(row,2)).strip(),
									'tt_se'        : str(sheet.cell_value(row,3)).strip(),
									'se'           : str(sheet.cell_value(row,4)).strip(),
									'ra_re'        : str(int(sheet.cell_value(row,5))).strip(),
									'rm_re'        : str(int(sheet.cell_value(row,6))).strip(),
									'tt_re'        : str(int(sheet.cell_value(row,7))).strip(),
									're'           : str(int(sheet.cell_value(row,8))).strip(),
									'ra_sg'        : str(int(sheet.cell_value(row,9))).strip(),
									'rm_sg'        : str(int(sheet.cell_value(row,10))).strip(),
									'tt_sg'        : str(int(sheet.cell_value(row,11))).strip(),
									'sg'           : str(int(sheet.cell_value(row,12))).strip(),
									'fm_fl'        : str(sheet.cell_value(row,13)).strip(),
									'fm_txt'       : str(sheet.cell_value(row,14)).strip(),
									'ord_talna_txt': str(sheet.cell_value(row,15)).strip(),
									'exam_code'    : exam_code,
									'exam_date'    : exam_date,
									'student_year' : student_year
								}
								if results:
									results.update(**results_dict)
								else:
									results = SamraemdMathResult.objects.create(**results_dict)
							else:
								#student missing
								pass #for now
			except Exception as e:
				return render(self.request, 'samraemd/form_import.html', {'error': 'Dálkur ekki til, reyndu aftur'})
		return redirect(self.get_success_url())

	def get_success_url(self):
		if 'school_id' in self.kwargs:
			return reverse_lazy('samraemd:math_listing', kwargs={'school_id': school_id},)	
		return reverse_lazy('samraemd:math_admin_listing')

	def test_func(self):
		return self.request.user.is_superuser

class SamraemdResultDelete(UserPassesTestMixin, DeleteView):
	model = SamraemdResult
	login_url = reverse_lazy('denied')
	template_name = "schools/confirm_delete.html"

	def test_func(self):
		return is_school_manager(self.request, self.kwargs)

	def get_success_url(self):
		return reverse_lazy('schools:school_listing')

	def get_object(self):
		return SamraemdResult.objects.filter(exam_name=self.kwargs['exam_name'])

class SamraemdMathResultDelete(UserPassesTestMixin, DeleteView):
	model = SamraemdMathResult
	login_url = reverse_lazy('denied')
	template_name = "schools/confirm_delete.html"

	def test_func(self):
		return is_school_manager(self.request, self.kwargs)

	def get_success_url(self):
		return reverse_lazy('schools:school_listing')

	def get_object(self):
		return SamraemdMathResult.objects.filter(exam_code=self.kwargs['exam_code'])

class SamraemdISLResultAdminListing(UserPassesTestMixin, ListView):
	model = SamraemdISLResult
	template_name = 'samraemd/samraemdresult_admin_list.html'

	def get_context_data(self, **kwargs):
		# xxx will be available in the template as the related objects
		context = super(SamraemdISLResultAdminListing, self).get_context_data(**kwargs)
		context['exams'] = SamraemdISLResult.objects.all().values('exam_date', 'student_year', 'exam_code').distinct()
		context['raw_exams'] = SamraemdResult.objects.filter(exam_code=1).values('exam_date', 'student_year', 'exam_name', 'exam_code').distinct()
		return context

	def test_func(self):
		return self.request.user.is_superuser

class SamraemdISLResultListing(UserPassesTestMixin, ListView):
	model = SamraemdISLResult

	def get_context_data(self, **kwargs):
		# xxx will be available in the template as the related objects
		context = super(SamraemdISLResultListing, self).get_context_data(**kwargs)
		school = School.objects.get(pk=self.kwargs['school_id'])
		context['exams'] = SamraemdISLResult.objects.filter(student__in = Student.objects.filter(school=school)).values('exam_code').distinct()
		context['school_id'] = school.id
		return context

	def test_func(self):
		return is_school_manager(self.request, self.kwargs) or is_school_teacher(self.request, self.kwargs)

class SamraemdISLResultCreate(UserPassesTestMixin, CreateView):
	model = SamraemdISLResult
	form_class = SamraemdISLResultForm		
	template_name = "samraemd/form_import.html"
	login_url = reverse_lazy('denied')

	def post(self, *args, **kwargs):
		if(self.request.FILES):
			u_file = self.request.FILES['file'].name
			extension = u_file.split(".")[-1]
			exam_code = self.request.POST.get('exam_code').strip()
			exam_date = self.request.POST.get('exam_date').strip()
			student_year = self.request.POST.get('student_year').strip()

			try:
				student_ssn=le_se=mn_se=ri_se=se=le_re=mn_re=ri_re=re=le_sg=mn_sg=ri_sg=sg=fm_fl=fm_txt=ord_talna_txt=''
				if extension.lower() == 'csv':
					for row in self.request.FILES['file'].readlines()[1:]:
						row = row.decode('utf-8')
						row = row.replace('"', '')
						row_data = row.split(',')
						student = Student.objects.filter(ssn=row_data[0].strip()) #student already exists
						if student:
							#check if results for student exists, create if not, otherwise update
							results = SamraemdISLResult.objects.filter(student=student, exam_code=exam_code)
							results_dict = {
								'student'     : student.first(),
								'le_se'       : row_data[1].strip(),
								'mn_se'       : row_data[2].strip(),
								'ri_se'       : row_data[3].strip(),
								'se'          : row_data[4].strip(),
								'le_re'       : row_data[5].strip(),
								'mn_re'       : row_data[6].strip(),
								'ri_re'       : row_data[7].strip(),
								're'          : row_data[8].strip(),
								'le_sg'       : row_data[9].strip(),
								'mn_sg'       : row_data[10].strip(),
								'ri_sg'       : row_data[11].strip(),
								'sg'          : row_data[12].strip(),
								'fm_fl'       : row_data[13].strip(),
								'fm_txt'      : row_data[14].strip(),
								'exam_code'   : exam_code,
								'exam_date'   : exam_date,
								'student_year': student_year
							}
							if results:
								results.update(**results_dict)
							else:
								results = SamraemdISLResult.objects.create(**results_dict)
						else:
							#student not found
							pass #for now
				elif extension == 'xlsx':
					input_excel = self.request.FILES['file']
					book        = xlrd.open_workbook(file_contents=input_excel.read())
					for sheetsnumber in range(book.nsheets):
						sheet = book.sheet_by_index(sheetsnumber)
						for row in range(1, sheet.nrows):
							student = Student.objects.filter(ssn=str(sheet.cell_value(row,0)).strip()) #student already exists
							if student:
								#check if results for student exists, create if not, otherwise update
								results      = SamraemdISLResult.objects.filter(student=student, exam_code=exam_code)
								results_dict = {
									'student'     : student.first(),
									'le_se'       : str(sheet.cell_value(row,1)).strip(),
									'mn_se'       : str(sheet.cell_value(row,2)).strip(),
									'ri_se'       : str(sheet.cell_value(row,3)).strip(),
									'se'          : str(sheet.cell_value(row,4)).strip(),
									'le_re'       : str(int(sheet.cell_value(row,5))).strip(),
									'mn_re'       : str(int(sheet.cell_value(row,6))).strip(),
									'ri_re'       : str(int(sheet.cell_value(row,7))).strip(),
									're'          : str(int(sheet.cell_value(row,8))).strip(),
									'le_sg'       : str(int(sheet.cell_value(row,9))).strip(),
									'mn_sg'       : str(int(sheet.cell_value(row,10))).strip(),
									'ri_sg'       : str(int(sheet.cell_value(row,11))).strip(),
									'sg'          : str(int(sheet.cell_value(row,12))).strip(),
									'fm_fl'       : str(sheet.cell_value(row,13)).strip(),
									'fm_txt'      : str(sheet.cell_value(row,14)).strip(),
									'exam_code'   : exam_code,
									'exam_date'   : exam_date,
									'student_year': student_year
								}
								if results:
									results.update(**results_dict)
								else:
									results = SamraemdISLResult.objects.create(**results_dict)
							else:
								#student not found
								pass #for now
			except Exception as e:
				return render(self.request, 'samraemd/form_import.html', {'error': 'Dálkur ekki til, reyndu aftur'})

		return redirect(self.get_success_url())

	def get_success_url(self):
		if 'school_id' in self.kwargs:
			return reverse_lazy('samraemd:isl_listing', kwargs={'school_id': school_id},)	
		return reverse_lazy('samraemd:isl_admin_listing')

	def test_func(self):
		return self.request.user.is_superuser

class SamraemdISLResultDelete(UserPassesTestMixin, DeleteView):
	model = SamraemdISLResult
	login_url = reverse_lazy('denied')
	template_name = "schools/confirm_delete.html"

	def test_func(self):
		return is_school_manager(self.request, self.kwargs)

	def get_success_url(self):
		return reverse_lazy('schools:school_listing')

	def get_object(self):
		return SamraemdISLResult.objects.filter(exam_code=self.kwargs['exam_code'])



class RawDataCreate(UserPassesTestMixin, CreateView):
	model         = SamraemdResult
	form_class    = SamraemdISLResultForm
	login_url     = reverse_lazy('denied')
	template_name = "samraemd/form_import_raw.html"

	def post(self, *args, **kwargs):
		row_offset = 4
		if(self.request.FILES):
			u_file        = self.request.FILES['file'].name
			extension     = u_file.split(".")[-1]
			exam_code     = self.request.POST.get('exam_code').strip()
			exam_name     = self.request.POST.get('exam_name').strip()
			exam_date     = self.request.POST.get('exam_date').strip()
			student_year  = self.request.POST.get('student_year').strip()
			result_length = self.request.POST.get('result_length').strip()

			try:
				input_excel = self.request.FILES['file']
				book        = xlrd.open_workbook(file_contents=input_excel.read())
				for sheetsnumber in range(book.nsheets):
					sheet = book.sheet_by_index(sheetsnumber)
					for row in range(row_offset, sheet.nrows):
						student = Student.objects.filter(ssn=str(sheet.cell_value(row,0)).strip()) #student already exists
						if student:
							#check if results for student exists, create if not, otherwise update
							result_data = get_results_from_sheet(sheet, row, result_length)
							results = SamraemdResult.objects.filter(student=student, exam_code=exam_code)
							results_dict = {
								'student'       : student.first(),
								'exam_code'     : exam_code,
								'exam_name'     : exam_name,
								'exam_date'     : exam_date,
								'student_year'  : student_year,
								'result_length' : result_length,
								'result_data'   : result_data
							}
							if results:
								results.update(**results_dict)
							else:
								results = SamraemdResult.objects.create(**results_dict)
						else:
							#student not found
							pass #for now
			except Exception as e:
				return render(self.request, 'samraemd/form_import_raw.html', {'error': 'Dálkur ekki til, reyndu aftur'})

		return redirect(self.get_success_url())

	def get_success_url(self):
		exam_code = self.request.POST.get('exam_code').strip()
		if '1' in exam_code:
			if 'school_id' in self.kwargs:
				return reverse_lazy('samraemd:isl_listing', kwargs={'school_id': school_id},)	
			return reverse_lazy('samraemd:isl_admin_listing')	
		if '3' in exam_code:
			if 'school_id' in self.kwargs:
				return reverse_lazy('samraemd:math_listing', kwargs={'school_id': school_id},)	
			return reverse_lazy('samraemd:math_admin_listing')	

	def test_func(self):
		return self.request.user.is_superuser



class SamraemdRawResultDetail(UserPassesTestMixin, DetailView):
	model = SamraemdResult

	def test_func(self):
		return is_school_manager(self.request, self.kwargs)

	def get_template_names(self, **kwargs):
		if 'einkunnablod' in self.request.path:
			return ['samraemd/samraemd_detail_raw_print_singles.html']
		return ['samraemd/samraemdresult_detail_raw.html']

	def get_object(self, **kwargs):
		return SamraemdMathResult.objects.first()

	def get_context_data(self, **kwargs):
		# xxx will be available in the template as the related objects
		context          = super(SamraemdRawResultDetail, self).get_context_data(**kwargs)
		year             = self.kwargs['year']
		context['year']  = year
		group            = self.kwargs['group']
		context['group'] = group
		student_results  = {}
		student_group    = {}
		col_names        = {}
		if 'school_id' in self.kwargs:
			school                 = School.objects.get(pk=self.kwargs['school_id'])
			context['school']      = school
			context['school_id']   = self.kwargs['school_id']
			context['school_name'] = school.name
			number_of_loops        = SamraemdResult.objects.all().values(
				'result_length','exam_code','exam_name').annotate(
				total=Count('exam_code')).filter(
				exam_date__year=year).filter(student_year=group)
			results                = SamraemdResult.objects.filter(
				student__in = Student.objects.filter(school=school)).filter(
				student_year=group).filter(exam_date__year=year)
			display_raw_results(results, student_results, student_group, col_names)

		else:
			if self.request.user.is_superuser:
				exam_code            = self.kwargs['exam_code']
				context['exam_code'] = exam_code
				number_of_loops      = SamraemdResult.objects.values(
					'result_length','exam_code','exam_name').filter(
					exam_code=exam_code,exam_date__year=year).annotate(total=Count('exam_code'))
				results              = SamraemdResult.objects.filter(
					exam_code=exam_code).filter(student_year=group).filter(exam_date__year=year)
				display_raw_results(results, student_results, student_group, col_names)

		context['student_results'] = student_results
		context['student_group']   = student_group
		context['loop_times']      = number_of_loops
		context['columns']         = col_names
		return context

def admin_result_raw_excel(request, exam_code, year, group):
	response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
	response['Content-Disposition'] = 'attachment; filename=hrániðurstöður-'+group+'.xlsx'
	number_of_loops = SamraemdResult.objects.filter(exam_code=exam_code,student_year=group,exam_date__year=year)[:1].values('result_length','exam_name').get()
	wb = openpyxl.Workbook()
	ws = wb.get_active_sheet()
	ws.title = number_of_loops['exam_name']

	ws['A1']=  'Skóli'
	ws['B1']=  'Kennitölur'
	ws['C1']=  'Nafn'
	ws['D1']=  'bekkur'
	# We need the first result just to get the keys for the columns
	first_result = SamraemdResult.objects.filter(exam_code=exam_code).filter(student_year=group).filter(exam_date__year=year).first().result_data.items()
	for key, result in first_result:
		ws.cell(row=1, column=int(key)+5).value =str(result['id'])

	index = 2
	for result in SamraemdResult.objects.filter(exam_code=exam_code).filter(student_year=group).filter(exam_date__year=year):
		ws.cell(row=index, column=1).value = str(School.objects.get(students=result.student).name)
		ws.cell(row=index, column=2).value = str(result.student.ssn)
		ws.cell(row=index, column=3).value = str(result.student)
		ws.cell(row=index, column=4).value = str(StudentGroup.objects.get(students=result.student))
		for key, values in result.result_data.items():
			ws.cell(row=index, column=int(key)+5).value = values['value']

		index +=1

	wb.save(response)

	return response

def excel_result_raw(request,school_id,   year, group):
	response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
	response['Content-Disposition'] = 'attachment; filename=hrániðurstöður-'+group+'.xlsx'
	wb = openpyxl.Workbook()
	number_of_loops =SamraemdResult.objects.all().values('result_length','exam_code','exam_name').annotate(total=Count('exam_code')).filter(exam_date__year=year).filter(student_year=group)
	for loops in number_of_loops:
		ws = wb.create_sheet()
		print(loops['exam_code'])
		if int(loops['exam_code']) == 1:
			ws.title = 'Íslenska'
		elif int(loops['exam_code']) == 2:
			ws.title = 'Enska'
		elif int(loops['exam_code']) == 3:
			ws.title = 'Stærðfræði'

		ws['A1']=  'Skóli'
		ws['B1']=  'Kennitölur'
		ws['C1']=  'Nafn'
		ws['D1']=  'bekkur'
		# We need the first result just to get the keys for the columns
		for result in SamraemdResult.objects.filter(student__in = Student.objects.filter(school=school_id)).filter(exam_code= loops['exam_code']).filter(student_year=group).filter(exam_date__year=year):
			for key, values in result.result_data.items():
				ws.cell(row=1, column=int(key)+5).value = values['id']
		index = 2
		for result in SamraemdResult.objects.filter(student__in = Student.objects.filter(school=school_id)).filter(exam_code= loops['exam_code']).filter(student_year=group).filter(exam_date__year=year):
			ws.cell(row=index, column=1).value = str(School.objects.get(students=result.student).name)
			ws.cell(row=index, column=2).value = str(result.student.ssn)
			ws.cell(row=index, column=3).value = str(result.student)
			ws.cell(row=index, column=4).value = str(StudentGroup.objects.get(students=result.student))
			for key, values in result.result_data.items():
				ws.cell(row=index, column=int(key)+5).value = values['value']

			index +=1

	wb.save(response)

	return response

