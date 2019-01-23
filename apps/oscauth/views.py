from django.shortcuts import render

def auth(request):
    
    return render(request, 'oscauth/auth.html', {

    })