import xml.etree.ElementTree as ET
from signxml import xmldsig

from django.apps import apps
from django.shortcuts import render, render_to_response, redirect
from django.conf import settings
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

from common.models import School

import requests, json

def verify_token(token):
	url = 'https://innskraning.mms.is/verify_login/'
	payload = {'token': token}
	r = requests.post(url, data=payload)
	return r.json()['verified']

@csrf_exempt
def index(request):
	if(request.method == "POST" and verify_token(request.POST.get('token'))):
		user = authenticate(username=request.POST['user_ssn'], password=request.POST['user_name'])
		if user == None:
			User.objects.create_user(username=request.POST['user_ssn'], password=request.POST['user_name'])
			user = authenticate(username=request.POST['user_ssn'], password=request.POST['user_name'])
		auth_login(request, user)
	return redirect('schools:school_listing')

def login(request):
	return redirect('denied')

def logout(request):
	auth_logout(request)
	return redirect('index')

def denied(request):
	return render(request, 'denied.html')
