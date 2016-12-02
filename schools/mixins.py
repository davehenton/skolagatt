from django.core.urlresolvers     import reverse_lazy, reverse
from django.contrib.auth.mixins   import UserPassesTestMixin

from .util import *

class SchoolEmployeeMixin(UserPassesTestMixin):
	login_url = reverse_lazy('denied')

	def test_func(self):
		return is_school_manager(self.request, self.kwargs) or is_school_teacher(self.request, self.kwargs)

class SchoolManagerMixin(UserPassesTestMixin):
	login_url = reverse_lazy('denied')

	def test_func(self):
		return is_school_manager(self.request, self.kwargs)

class SchoolTeacherMixin(UserPassesTestMixin):
	login_url = reverse_lazy('denied')

class SuperUserMixin(UserPassesTestMixin):
	success_url = reverse_lazy('schools:school_listing')
	login_url = reverse_lazy('denied')

	def test_func(self):
		return self.request.user.is_superuser