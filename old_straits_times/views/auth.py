from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect
from django.urls import reverse

from django.core.validators import validate_email
from django.contrib.auth.password_validation import validate_password

from ..models import Author

import re

def auth_login(request):
    template_name = 'old_straits_times/auth/login.html'
    
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse('oldstimes:index'))
    
    context = {
        'success_message': '',
        'error_message': ''
    }
    
    if request.GET.get('m', '') == 'reg_success':
        context['success_message'] = 'Register sucessfully! Please login your account.'
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse('oldstimes:index'))
        else:
            context['error_message'] = 'Username or password incorrect.'
    
    return render(request, template_name, context)

def auth_logout(request):    
    logout(request)
    
    return HttpResponseRedirect(reverse('oldstimes:index'))

def auth_register(request):
    template_name = 'old_straits_times/auth/register.html'
    
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse('oldstimes:index'))
    
    if request.method == 'POST':
        first_name:str = request.POST.get('first_name')
        last_name:str = request.POST.get('last_name')
        username:str = request.POST.get('username')
        email:str = request.POST.get('email')
        password:str = request.POST.get('password')
        confirmation_password:str = request.POST.get('confirmation_password')
        
        # check username
        if not re.match(r'[a-zA-Z0-9@.+-_]{8,20}', username):
            return render(request, template_name, {
                'error_message': "The username does not meet criteria!"
            })
            
        if Author.objects.filter(username=username).exists():
            return render(request, template_name, {
                'error_message': "The username has been used! Try another username."
            })
        
        # check email address
        try:
            validate_email(email)
        except:
            return render(request, template_name, {
                'error_message': "Invalid email address!"
            })
            
        if Author.objects.filter(email=email).exists():
            return render(request, template_name, {
                'error_message': "The email address has been used!"
            })
        
        # check password
        try:
            validate_password(password)
        except:
            return render(request, template_name, {
                'error_message': "Invalid password!"
            })
        
        # check confirmation password
        if confirmation_password != password:
            return render(request, template_name, {
                'error_message': "Password not match!"
            })
            
        new_author = Author.objects.create(
            first_name=first_name,
            last_name=last_name,
            username=username,
            email=email
        )
        new_author.set_password(password)
        new_author.save()
        
        return HttpResponseRedirect('%s?m=reg_success' % reverse('oldstimes:auth_login'))
        
    return render(request, template_name, {})
