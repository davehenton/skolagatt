from django.apps import apps
from django.shortcuts import render, render_to_response, redirect
from django.conf import settings
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout

def index(request):
    return render(request, 'index.html')

def login(request):
    user = authenticate(username=request.POST['username'], password=request.POST['password'])
    if user is not None:
        if user.is_active:
            auth_login(request, user)
            return redirect('index')
    return redirect('auth_login')

def logout(request):
    auth_logout(request)
    return redirect('index')

def denied(request):
    return render(request, 'denied.html')