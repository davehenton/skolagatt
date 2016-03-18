from django.apps import apps
from django.shortcuts import render, render_to_response, redirect
from django.conf import settings
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout

from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required

def index(request):
    return render(request, 'index.html')

@csrf_exempt
@login_required
def login(request):
    if(request.method == "POST"):
        user = authenticate(username=request.POST['user_ssn'], password=request.POST['user_name'])
        if user is not None:
            if user.is_active:
                auth_login(request, user)
                return redirect('index')
    return redirect('denied')

def logout(request):
    auth_logout(request)
    return redirect('index')

def denied(request):
    return render(request, 'denied.html')