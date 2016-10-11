from django.shortcuts import render

from common.models import *
from .models import *

from django.shortcuts import render, render_to_response, get_object_or_404, redirect
from django.contrib.auth.mixins import UserPassesTestMixin
from django.views.generic import ListView, CreateView, DetailView, UpdateView, DeleteView
from django.core.urlresolvers import reverse_lazy, reverse

import xlrd
from itertools import chain

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

class SamraemdResultListing(UserPassesTestMixin, ListView):
	model = SamraemdMathResult
	template_name = 'samraemd/samraemdschoolresult_list.html'

	def get_context_data(self, **kwargs):
		# xxx will be available in the template as the related objects
		context = super(SamraemdResultListing, self).get_context_data(**kwargs)
		school = School.objects.get(pk=self.kwargs['school_id'])
		m_exams = SamraemdMathResult.objects.filter(student__in = Student.objects.filter(school=school)).values('exam_date', 'student_year', 'exam_code').distinct()
		i_exams = SamraemdISLResult.objects.filter(student__in = Student.objects.filter(school=school)).values('exam_date', 'student_year', 'exam_code').distinct()
		context['exams'] = list(chain(m_exams, i_exams))
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
		return ['samraemd/samraemdmathresult_detail.html']

	def get_object(self, **kwargs):
		return SamraemdMathResult.objects.first()

	def get_context_data(self, **kwargs):
		# xxx will be available in the template as the related objects
		context = super(SamraemdResultDetail, self).get_context_data(**kwargs)
		year = self.kwargs['year']
		context['year'] = year
		group = self.kwargs['group']
		if 'school_id' in self.kwargs:
			school = School.objects.get(pk=self.kwargs['school_id'])
			context['group'] = StudentGroup.objects.get(pk=group)
			context['school_id'] = self.kwargs['school_id']
			context['school_name'] = school.name
			student_results = {}
			for result in list(chain(
				SamraemdISLResult.objects.filter(student__in = Student.objects.filter(school=school)).filter(student_year=group).filter(exam_date__year=year),
				SamraemdMathResult.objects.filter(student__in = Student.objects.filter(school=school)).filter(student_year=group).filter(exam_date__year=year),
				)):
				if result.student in student_results:
					student_results[result.student].append(result)
				else:
					student_results[result.student] = [result]
			context['student_results'] = student_results
		#else:
			#context['exam_results'] = SamraemdMathResult.objects.filter(exam_code=self.kwargs['exam_code'])
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
							if results:
								results.update(
									student=student.first(),
									ra_se = row_data[1].strip(),
									rm_se = row_data[2].strip(),
									tt_se=row_data[3].strip(),
									se=row_data[4].strip(),
									ra_re=row_data[5].strip(),
									rm_re=row_data[6].strip(),
									tt_re=row_data[7].strip(),
									re=row_data[8].strip(),
									ra_sg=row_data[9].strip(),
									rm_sg=row_data[10].strip(),
									tt_sg=row_data[11].strip(),
									sg=row_data[12].strip(),
									fm_fl=row_data[13].strip(),
									fm_txt=row_data[14].strip(),
									ord_talna_txt=row_data[15].strip(),
									exam_code=exam_code,
									exam_date=exam_date,
									student_year=student_year,
									)
							else:
								results = SamraemdMathResult.objects.create(
									student=student.first(),
									ra_se = row_data[1].strip(),
									rm_se = row_data[2].strip(),
									tt_se=row_data[3].strip(),
									se=row_data[4].strip(),
									ra_re=row_data[5].strip(),
									rm_re=row_data[6].strip(),
									tt_re=row_data[7].strip(),
									re=row_data[8].strip(),
									ra_sg=row_data[9].strip(),
									rm_sg=row_data[10].strip(),
									tt_sg=row_data[11].strip(),
									sg=row_data[12].strip(),
									fm_fl=row_data[13].strip(),
									fm_txt=row_data[14].strip(),
									ord_talna_txt=row_data[15].strip(),
									exam_code=exam_code,
									exam_date=exam_date,
									student_year=student_year,
									)
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
								if results:
									results.update(
										student=student.first(),
										ra_se = str(sheet.cell_value(row,1)).strip(),
										rm_se = str(sheet.cell_value(row,2)).strip(),
										tt_se = str(sheet.cell_value(row,3)).strip(),
										se = str(sheet.cell_value(row,4)).strip(),
										ra_re = str(int(sheet.cell_value(row,5))).strip(),
										rm_re = str(int(sheet.cell_value(row,6))).strip(),
										tt_re = str(int(sheet.cell_value(row,7))).strip(),
										re = str(int(sheet.cell_value(row,8))).strip(),
										ra_sg = str(int(sheet.cell_value(row,9))).strip(),
										rm_sg = str(int(sheet.cell_value(row,10))).strip(),
										tt_sg = str(int(sheet.cell_value(row,11))).strip(),
										sg = str(int(sheet.cell_value(row,12))).strip(),
										fm_fl = str(sheet.cell_value(row,13)).strip(),
										fm_txt = str(sheet.cell_value(row,14)).strip(),
										ord_talna_txt = str(sheet.cell_value(row,15)).strip(),
										exam_code = exam_code,
										exam_date = exam_date,
										student_year = student_year,
										)
								else:
									results = SamraemdMathResult.objects.create(
										student=student.first(),
										ra_se = str(sheet.cell_value(row,1)).strip(),
										rm_se = str(sheet.cell_value(row,2)).strip(),
										tt_se = str(sheet.cell_value(row,3)).strip(),
										se = str(sheet.cell_value(row,4)).strip(),
										ra_re = str(int(sheet.cell_value(row,5))).strip(),
										rm_re = str(int(sheet.cell_value(row,6))).strip(),
										tt_re = str(int(sheet.cell_value(row,7))).strip(),
										re = str(int(sheet.cell_value(row,8))).strip(),
										ra_sg = str(int(sheet.cell_value(row,9))).strip(),
										rm_sg = str(int(sheet.cell_value(row,10))).strip(),
										tt_sg = str(int(sheet.cell_value(row,11))).strip(),
										sg = str(int(sheet.cell_value(row,12))).strip(),
										fm_fl = str(sheet.cell_value(row,13)).strip(),
										fm_txt = str(sheet.cell_value(row,14)).strip(),
										ord_talna_txt = str(sheet.cell_value(row,15)).strip(),
										exam_code = exam_code,
										exam_date = exam_date,
										student_year = student_year,
										)
							else:
								#student missing
								pass #for now						
			except Exception as e:
				print(e)
				return render(self.request, 'samraemd/form_import.html', {'error': 'Dálkur ekki til, reyndu aftur'})
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
							if results:
								results.update(
									student=student.first(),
									le_se = row_data[1].strip(),
									mn_se = row_data[2].strip(),
									ri_se = row_data[3].strip(),
									se = row_data[4].strip(),
									le_re = row_data[5].strip(),
									mn_re = row_data[6].strip(),
									ri_re = row_data[7].strip(),
									re = row_data[8].strip(),
									le_sg = row_data[9].strip(),
									mn_sg = row_data[10].strip(),
									ri_sg = row_data[11].strip(),
									sg = row_data[12].strip(),
									fm_fl = row_data[13].strip(),
									fm_txt = row_data[14].strip(),
									exam_code = exam_code,
									exam_date = exam_date,
									student_year = student_year,
									)
							else:
								results = SamraemdISLResult.objects.create(
									student=student.first(),
									le_se = row_data[1].strip(),
									mn_se = row_data[2].strip(),
									ri_se = row_data[3].strip(),
									se = row_data[4].strip(),
									le_re = row_data[5].strip(),
									mn_re = row_data[6].strip(),
									ri_re = row_data[7].strip(),
									re = row_data[8].strip(),
									le_sg = row_data[9].strip(),
									mn_sg = row_data[10].strip(),
									ri_sg = row_data[11].strip(),
									sg = row_data[12].strip(),
									fm_fl = row_data[13].strip(),
									fm_txt = row_data[14].strip(),
									exam_code = exam_code,
									exam_date = exam_date,
									student_year = student_year,
									)
						else:
							#student not found
							pass #for now						
				elif extension == 'xlsx':
					input_excel = self.request.FILES['file']
					book = xlrd.open_workbook(file_contents=input_excel.read())
					for sheetsnumber in range(book.nsheets):
						sheet = book.sheet_by_index(sheetsnumber)
						for row in range(1, sheet.nrows):
							student = Student.objects.filter(ssn=str(sheet.cell_value(row,0)).strip()) #student already exists
							if student:
								#check if results for student exists, create if not, otherwise update
								results = SamraemdISLResult.objects.filter(student=student, exam_code=exam_code)
								if results:
									results.update(
										student=student.first(),
										le_se = str(sheet.cell_value(row,1)).strip(),
										mn_se = str(sheet.cell_value(row,2)).strip(),
										ri_se = str(sheet.cell_value(row,3)).strip(),
										se = str(sheet.cell_value(row,4)).strip(),
										le_re = str(int(sheet.cell_value(row,5))).strip(),
										mn_re = str(int(sheet.cell_value(row,6))).strip(),
										ri_re = str(int(sheet.cell_value(row,7))).strip(),
										re = str(int(sheet.cell_value(row,8))).strip(),
										le_sg = str(int(sheet.cell_value(row,9))).strip(),
										mn_sg = str(int(sheet.cell_value(row,10))).strip(),
										ri_sg = str(int(sheet.cell_value(row,11))).strip(),
										sg = str(int(sheet.cell_value(row,12))).strip(),
										fm_fl = str(sheet.cell_value(row,13)).strip(),
										fm_txt = str(sheet.cell_value(row,14)).strip(),
										exam_code = exam_code,
										exam_date = exam_date,
										student_year = student_year,
										)
								else:
									results = SamraemdISLResult.objects.create(
										student=student.first(),
										le_se = str(sheet.cell_value(row,1)).strip(),
										mn_se = str(sheet.cell_value(row,2)).strip(),
										ri_se = str(sheet.cell_value(row,3)).strip(),
										se = str(sheet.cell_value(row,4)).strip(),
										le_re = str(int(sheet.cell_value(row,5))).strip(),
										mn_re = str(int(sheet.cell_value(row,6))).strip(),
										ri_re = str(int(sheet.cell_value(row,7))).strip(),
										re = str(int(sheet.cell_value(row,8))).strip(),
										le_sg = str(int(sheet.cell_value(row,9))).strip(),
										mn_sg = str(int(sheet.cell_value(row,10))).strip(),
										ri_sg = str(int(sheet.cell_value(row,11))).strip(),
										sg = str(int(sheet.cell_value(row,12))).strip(),
										fm_fl = str(sheet.cell_value(row,13)).strip(),
										fm_txt = str(sheet.cell_value(row,14)).strip(),
										exam_code = exam_code,
										exam_date = exam_date,
										student_year = student_year,
										)
							else:
								#student not found
								pass #for now
			except Exception as e:
				print(e)
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