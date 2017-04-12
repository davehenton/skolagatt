from django.shortcuts import render, redirect
from django.conf import settings
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.http import JsonResponse
from uuid import uuid4

from common.models import Manager, Teacher
from common import util

import requests
import os

from common.models import ExampleSurveyQuestion


def verify_token(token):
    url = settings.ICEKEY_VERIFICATION
    payload = {'token': token}
    try:
        r = requests.post(url, data=payload, headers=dict(Referer=url))
        return r.json()['verified']
    except:
        pass
    return False


@csrf_exempt
def index(request):
    return redirect('schools:school_listing')


@csrf_exempt
def login(request):
    if settings.DEBUG:
        if(request.method == "POST"):
            user = User.objects.filter(username=request.POST['user_ssn'])
            if user.exists():
                user = authenticate(username=user.first().username)
                auth_login(request, user)
                if util.is_manager(request):
                    return redirect(
                        'schools:manager_overview',
                        Manager.objects.filter(user=request.user).first().id)
                elif util.is_teacher(request):
                    return redirect(
                        'schools:teacher_overview',
                        Teacher.objects.filter(user=request.user).first().id)
                return redirect('schools:school_listing')
        return render(request, 'local_login.html')
    else:
        if(request.method == "POST" and verify_token(request.POST.get('token'))):
            user = User.objects.filter(username=request.POST['user_ssn'])
            # get or create user
            if user.exists():
                user = user.first()
            else:
                # remove this feature and add no user error. ???
                user = User.objects.create_user(
                    username=request.POST['user_ssn'],
                    password=str(uuid4())
                )
            # authenticate user
            user = authenticate(username=user.username)
            auth_login(request, user)
            if util.is_manager(request):
                return redirect(
                    'schools:manager_overview',
                    Manager.objects.filter(user=request.user).first().id)
            elif util.is_teacher(request):
                return redirect(
                    'schools:teacher_overview',
                    Teacher.objects.filter(user=request.user).first().id)
            return redirect('schools:school_listing')
        else:
            context = {
                'icekey_verification': settings.ICEKEY_VERIFICATION,
                'icekey_login': settings.ICEKEY_LOGIN
            }
            return render(request, 'login.html', context)


def logout(request):
    auth_logout(request)
    return redirect('index')


def denied(request):
    return render(request, 'denied.html')


def images(request):
    image_dir = os.path.join(settings.BASE_DIR, settings.FROALA_UPLOAD_PATH)
    context = []
    for filename in os.listdir(image_dir):
        if not os.path.splitext(filename)[-1].lower() in ['.jpg', '.png', '.jpeg']:
            continue
        tag = [x[1] for x in ExampleSurveyQuestion.category_choices if x[0] == filename[:2]][0]
        if not tag:
            tag = 'unknown'

        context.append({
            'url': os.path.join('/' + settings.FROALA_UPLOAD_PATH, filename),
            'thumb': os.path.join('/' + settings.FROALA_UPLOAD_PATH, filename),
            'tag': tag,
        })
    return JsonResponse(context, safe=False)
