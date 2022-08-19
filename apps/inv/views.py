from django.shortcuts import render

def base(request):
    context = {'test':'Hello World'}
    template = 'inv/base.html'
    return render(request,template,context)