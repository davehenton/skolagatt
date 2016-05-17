import xml.etree.ElementTree as ET
from signxml import xmldsig

from django.apps import apps
from django.shortcuts import render, render_to_response, redirect, HttpResponseRedirect
from django.conf import settings
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from uuid import uuid4

from common.models import School

import requests, json

def verify_token(token):
	url = 'https://innskraning.mms.is/verify_login/'
	payload = {'token': token}
	r = requests.post(url, data=payload, headers=dict(Referer=url))
	return r.json()['verified']

@csrf_exempt
def index(request):
	return redirect('schools:school_listing')

@csrf_exempt
def login(request):
	if(request.method == "POST" and verify_token(request.POST.get('token'))):
		user = User.objects.filter(username=request.POST['user_ssn'])
		#get or create user
		if user.exists():
			user = user.first()
		else:
			#remove this feature and add no user error. ???
			user = User.objects.create_user(username=request.POST['user_ssn'], password=str(uuid4()))

		#authenticate user
		user = authenticate(user.username)
		auth_login(request, user, backend=backend)
		return redirect('schools:school_listing')
	else:
		return render(request, 'login.html')

def logout(request):
	auth_logout(request)
	return redirect('index')

def denied(request):
	return render(request, 'denied.html')
