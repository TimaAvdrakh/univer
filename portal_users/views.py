from django.shortcuts import render
from django.contrib.auth import authenticate, login
from django.shortcuts import HttpResponse
from . import forms
from django.contrib import messages


def auth(request):
    form = forms.LoginForm()
    if request.method == 'POST':
        form = forms.LoginForm(data=request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user = authenticate(username=cd['username'],
                                password=cd['password'])
            if user:
                if user.is_active:
                    login(request, user)
                    return render(request,
                                  'test.html')
                else:
                    messages.error(request,
                                   'Пользователь не активен')
            else:
                messages.error(request,
                               'Неверный логин или пароль')

    return render(request,
                  'login.html',
                  context={'form': form})
