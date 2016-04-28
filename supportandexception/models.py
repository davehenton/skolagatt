# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.db import models

from common.models import *



# undanþágur
class Exceptions(models.Model):
	student = models.ForeignKey(Student)
	reason = models.CharField(max_length = 1)
	exam = models.CharField(max_length = 1)
	explanation = models.CharField(max_length = 500)
	signature = models.CharField(max_length = 140)
	date = models.DateField(auto_now=False,auto_now_add=True, null=True)

	def __str__(self):
		return self.reason


# Stuðningsúrræði

class SupportResource(models.Model):
	student = models.ForeignKey(Student)
	explanation = models.CharField(max_length = 500)
	signature = models.CharField(max_length = 140)
	date = models.DateField(auto_now = True, null = True)
	support_title = models.CharField(max_length = 1,null=True)
	reading_assistance = models.CharField(max_length = 1,null=True)
	interpretation = models.CharField(max_length = 1,null=True)
	return_to_sites = models.CharField(max_length = 1,null=True)
	longer_time = models.CharField(max_length = 1,null=True)
	def __str__(self):
		return self.student
