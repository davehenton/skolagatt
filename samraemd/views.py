from django.shortcuts import render

from common.models import *
from .models import *

from django.shortcuts import render, render_to_response, get_object_or_404, redirect
from django.contrib.auth.mixins import UserPassesTestMixin
from django.views.generic import ListView, CreateView, DetailView, UpdateView, DeleteView
from django.core.urlresolvers import reverse_lazy, reverse

import xlrd

from schools.util import *

class SamraemdMathResultAdminListing(UserPassesTestMixin, ListView):
	model = SamraemdMathResult
	template_name = 'samraemd/samraemdmathresult_admin_list.html'

	def get_context_data(self, **kwargs):
		# xxx will be available in the template as the related objects
		context = super(SamraemdMathResultAdminListing, self).get_context_data(**kwargs)
		context['exams'] = SamraemdMathResult.objects.all().values('exam_code').distinct()
		return context

	def test_func(self):
		return self.request.user.is_superuser

class SamraemdMathResultListing(UserPassesTestMixin, ListView):
	model = SamraemdMathResult

	def get_context_data(self, **kwargs):
		# xxx will be available in the template as the related objects
		context = super(SamraemdMathResultListing, self).get_context_data(**kwargs)
		school = School.objects.get(pk=self.kwargs['school_id'])
		context['exams'] = SamraemdMathResult.objects.filter(student__in = Student.objects.filter(school=school)).values('exam_code').distinct()
		context['school_id'] = school.id
		return context

	def test_func(self):
		return is_school_manager(self.request, self.kwargs) or is_school_teacher(self.request, self.kwargs)

class SamraemdMathResultDetail(UserPassesTestMixin, DetailView):
	model = SamraemdMathResult

	def test_func(self):
		return is_school_manager(self.request, self.kwargs)

	def get_template_names(self, **kwargs):
		if 'print' in self.kwargs:
			if self.kwargs['print'] == 'listi':
				return ['samraemd/surveylogin_detail_print_list.html']
			elif self.kwargs['print'] == 'einstaklingsblod':
				return ['samraemd/surveylogin_detail_print_singles.html']
		return ['samraemd/samraemdmathresult_detail.html']

	def get_object(self, **kwargs):
		return SamraemdMathResult.objects.filter(exam_code=self.kwargs['exam_code']).first()

	def get_context_data(self, **kwargs):
		# xxx will be available in the template as the related objects
		context = super(SamraemdMathResultDetail, self).get_context_data(**kwargs)
		context['exam_code'] = self.kwargs['exam_code']
		if 'school_id' in self.kwargs:
			school = School.objects.get(pk=self.kwargs['school_id'])
			context['school_id'] = self.kwargs['school_id']
			context['exam_results'] = SamraemdMathResult.objects.filter(student__in = Student.objects.filter(school=school)).filter(exam_code=self.kwargs['exam_code'])
		else:
			context['exam_results'] = SamraemdMathResult.objects.filter(exam_code=self.kwargs['exam_code'])
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

			data = []
			try:
				if extension.lower() == 'csv':
					for row in self.request.FILES['file'].readlines()[1:]:
						row = row.decode('utf-8')
						row = row.replace('"', '')
						row_data = row.split(',')
						data.append({
							'student': row_data[0].strip(),
							'ra_se': row_data[1].strip(),
							'rm_se': row_data[2].strip(),
							'tt_se': row_data[3].strip(),
							'se': row_data[4].strip(),
							#Raðeinkunn
							'ra_re': row_data[5].strip(),
							'rm_re': row_data[6].strip(),
							'tt_re': row_data[7].strip(),
							're': row_data[8].strip(),
							#Grunnskólaeinkunn
							'ra_sg': row_data[9].strip(),
							'rm_sg': row_data[10].strip(),
							'tt_sg': row_data[11].strip(),
							'sg': row_data[12].strip(),
							#Framfaraeinkunn	
							'fm_fl': row_data[13].strip(),
							'fm_txt': row_data[14].strip(),						
							#exam fields
							'ord_talna_txt': row_data[15].strip(),
							'exam_code': exam_code,
							'exam_date': exam_date
							})
				elif extension == 'xlsx':
					input_excel = self.request.FILES['file']
					book = xlrd.open_workbook(file_contents=input_excel.read())
					for sheetsnumber in range(book.nsheets):
						sheet = book.sheet_by_index(sheetsnumber)
						for row in range(1, sheet.nrows):
							data.append({
								'student': str(sheet.cell_value(row,0)).strip(),
								'ra_se': str(sheet.cell_value(row,1)).strip(),
								'rm_se': str(sheet.cell_value(row,2)).strip(),
								'tt_se': str(sheet.cell_value(row,3)).strip(),
								'se': str(sheet.cell_value(row,4)).strip(),
								#Raðeinkunn
								'ra_re': str(int(sheet.cell_value(row,5))).strip(),
								'rm_re': str(int(sheet.cell_value(row,6))).strip(),
								'tt_re': str(int(sheet.cell_value(row,7))).strip(),
								're': str(int(sheet.cell_value(row,8))).strip(),
								#Grunnskólaeinkunn
								'ra_sg': str(int(sheet.cell_value(row,9))).strip(),
								'rm_sg': str(int(sheet.cell_value(row,10))).strip(),
								'tt_sg': str(int(sheet.cell_value(row,11))).strip(),
								'sg': str(int(sheet.cell_value(row,12))).strip(),
								#Framfaraeinkunn	
								'fm_fl': str(sheet.cell_value(row,13)).strip(),
								'fm_txt': str(sheet.cell_value(row,14)).strip(),		
								#exam fields
								'ord_talna_txt': str(sheet.cell_value(row,15)).strip(),
								'exam_code': exam_code,
								'exam_date': exam_date							
								})
				return render(self.request, 'samraemd/math_verify_import.html', {'data': data})
			except Exception as e:
				print(e)
				return render(self.request, 'samraemd/form_import.html', {'error': 'Dálkur ekki til, reyndu aftur'})
		else:
			student_data = json.loads(self.request.POST['students'])
			#iterate through the data, add students if they don't exist then create a survey_login object
			for data in student_data:
				student = Student.objects.filter(ssn=data['student']) #student already exists
				if student:
					#check if results for student exists, create if not, otherwise update
					results = SamraemdMathResult.objects.filter(student=student, exam_code=data['exam_code'])
					if results:
						results.update(
							student=Student.objects.get(ssn=data['student']),
							ra_se=data['ra_se'],
							rm_se=data['rm_se'],
							tt_se=data['tt_se'],
							se=data['se'],
							ra_re=data['ra_re'],
							rm_re=data['rm_re'],
							tt_re=data['tt_re'],
							re=data['re'],
							ra_sg=data['ra_sg'],
							rm_sg=data['rm_sg'],
							tt_sg=data['tt_sg'],
							sg=data['sg'],
							fm_fl=data['fm_fl'],
							fm_txt=data['fm_txt'],
							ord_talna_txt=data['ord_talna_txt'],
							exam_code=data['exam_code'],
							exam_date=data['exam_date'],
							)
					else:
						results = SamraemdMathResult.objects.create(
							student=Student.objects.get(ssn=data['student']),
							ra_se=data['ra_se'],
							rm_se=data['rm_se'],
							tt_se=data['tt_se'],
							se=data['se'],
							ra_re=data['ra_re'],
							rm_re=data['rm_re'],
							tt_re=data['tt_re'],
							re=data['re'],
							ra_sg=data['ra_sg'],
							rm_sg=data['rm_sg'],
							tt_sg=data['tt_sg'],
							sg=data['sg'],
							fm_fl=data['fm_fl'],
							fm_txt=data['fm_txt'],							
							ord_talna_txt=data['ord_talna_txt'],
							exam_code=data['exam_code'],
							exam_date=data['exam_date'],
							)
		return redirect(self.get_success_url())

	def get_success_url(self):
		if 'school_id' in self.kwargs:
			return reverse_lazy('samraemd:math_listing', kwargs={'school_id': school_id},)	
		return reverse_lazy('samraemd:math_admin_listing')

	def test_func(self):
		return self.request.user.is_superuser

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
	template_name = 'samraemd/samraemdmathresult_admin_list.html'

	def get_context_data(self, **kwargs):
		# xxx will be available in the template as the related objects
		context = super(SamraemdISLResultAdminListing, self).get_context_data(**kwargs)
		context['exams'] = SamraemdISLResult.objects.all().values('exam_code').distinct()
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

class SamraemdISLResultDetail(UserPassesTestMixin, DetailView):
	model = SamraemdISLResult

	def test_func(self):
		return is_school_manager(self.request, self.kwargs)

	def get_template_names(self, **kwargs):
		if 'print' in self.kwargs:
			if self.kwargs['print'] == 'listi':
				return ['samraemd/surveylogin_detail_print_list.html']
			elif self.kwargs['print'] == 'einstaklingsblod':
				return ['samraemd/surveylogin_detail_print_singles.html']
		return ['samraemd/samraemdislresult_detail.html']

	def get_object(self, **kwargs):
		return SamraemdISLResult.objects.filter(exam_code=self.kwargs['exam_code']).first()

	def get_context_data(self, **kwargs):
		# xxx will be available in the template as the related objects
		context = super(SamraemdISLResultDetail, self).get_context_data(**kwargs)
		context['exam_code'] = self.kwargs['exam_code']
		if 'school_id' in self.kwargs:
			school = School.objects.get(pk=self.kwargs['school_id'])
			context['school_id'] = self.kwargs['school_id']
			context['exam_results'] = SamraemdISLResult.objects.filter(student__in = Student.objects.filter(school=school)).filter(exam_code=self.kwargs['exam_code'])
		else:
			context['exam_results'] = SamraemdISLResult.objects.filter(exam_code=self.kwargs['exam_code'])
		return context

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

			data = []
			try:
				if extension.lower() == 'csv':
					for row in self.request.FILES['file'].readlines()[1:]:
						row = row.decode('utf-8')
						row = row.replace('"', '')
						row_data = row.split(',')
						data.append({
							'student': row_data[0].strip(),
							'le_se': row_data[1].strip(),
							'mn_se': row_data[2].strip(),
							'ri_se': row_data[3].strip(),
							'se': row_data[4].strip(),
							#Raðeinkunn
							'le_re': row_data[5].strip(),
							'mn_re': row_data[6].strip(),
							'ri_re': row_data[7].strip(),
							're': row_data[8].strip(),
							#Grunnskólaeinkunn
							'le_sg': row_data[9].strip(),
							'mn_sg': row_data[10].strip(),
							'ri_sg': row_data[11].strip(),
							'sg': row_data[12].strip(),
							'fm_fl': row_data[13].strip(),
							'fm_txt': row_data[14].strip(),
							#exam fields
							'exam_code': exam_code,
							'exam_date': exam_date
							})
				elif extension == 'xlsx':
					input_excel = self.request.FILES['file']
					book = xlrd.open_workbook(file_contents=input_excel.read())
					for sheetsnumber in range(book.nsheets):
						sheet = book.sheet_by_index(sheetsnumber)
						for row in range(1, sheet.nrows):
							data.append({
								'student': str(sheet.cell_value(row,0)).strip(),
								'le_se': str(sheet.cell_value(row,1)).strip(),
								'mn_se': str(sheet.cell_value(row,2)).strip(),
								'ri_se': str(sheet.cell_value(row,3)).strip(),
								'se': str(sheet.cell_value(row,4)).strip(),
								#Raðeinkunn
								'le_re': str(int(sheet.cell_value(row,5))).strip(),
								'mn_re': str(int(sheet.cell_value(row,6))).strip(),
								'ri_re': str(int(sheet.cell_value(row,7))).strip(),
								're': str(int(sheet.cell_value(row,8))).strip(),
								#Grunnskólaeinkunn
								'le_sg': str(int(sheet.cell_value(row,9))).strip(),
								'mn_sg': str(int(sheet.cell_value(row,10))).strip(),
								'ri_sg': str(int(sheet.cell_value(row,11))).strip(),
								'sg': str(int(sheet.cell_value(row,12))).strip(),
								'fm_fl': str(sheet.cell_value(row,13)).strip(),
								'fm_txt': str(sheet.cell_value(row,14)).strip(),
								#exam fields
								'exam_code': exam_code,
								'exam_date': exam_date							
								})
				return render(self.request, 'samraemd/isl_verify_import.html', {'data': data})
			except Exception as e:
				print(e)
				return render(self.request, 'samraemd/form_import.html', {'error': 'Dálkur ekki til, reyndu aftur'})
		else:
			student_data = json.loads(self.request.POST['students'])
			#iterate through the data, add students if they don't exist then create a survey_login object
			for data in student_data:
				student = Student.objects.filter(ssn=data['student']) #student already exists
				if student:
					#check if results for student exists, create if not, otherwise update
					results = SamraemdISLResult.objects.filter(student=student, exam_code=data['exam_code'])
					if results:
						results.update(
							student=Student.objects.get(ssn=data['student']),
							le_se=data['le_se'],
							mn_se=data['mn_se'],
							ri_se=data['ri_se'],
							se=data['se'],
							le_re=data['le_re'],
							mn_re=data['mn_re'],
							ri_re=data['ri_re'],
							re=data['re'],
							le_sg=data['le_sg'],
							mn_sg=data['mn_sg'],
							ri_sg=data['ri_sg'],
							sg=data['sg'],
							fm_fl=data['fm_fl'],
							fm_txt=data['fm_txt'],								
							exam_code=data['exam_code'],
							exam_date=data['exam_date'],
							)
					else:
						results = SamraemdISLResult.objects.create(
							student=Student.objects.get(ssn=data['student']),
							le_se=data['le_se'],
							mn_se=data['mn_se'],
							ri_se=data['ri_se'],
							se=data['se'],
							le_re=data['le_re'],
							mn_re=data['mn_re'],
							ri_re=data['ri_re'],
							re=data['re'],
							le_sg=data['le_sg'],
							mn_sg=data['mn_sg'],
							ri_sg=data['ri_sg'],
							sg=data['sg'],
							fm_fl=data['fm_fl'],
							fm_txt=data['fm_txt'],								
							exam_code=data['exam_code'],
							exam_date=data['exam_date'],
							)
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