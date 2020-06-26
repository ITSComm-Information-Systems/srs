# osc\pages\view
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect

from . models import Page


def index(request, pagename):
    pagename = '/' + pagename
    pg = get_object_or_404(Page, permalink=pagename)
    context = {
        'title': pg.title,
        'content': pg.bodytext,
        'last_updated': pg.update_date,
        'page_list':  Page.objects.all(),
    }
    # assert False
    if pagename[1:5] == 'apps':
        return render(request, 'baseapps.html', context)
    else:
        return render(request, 'base.html', context)
    return render(request, 'base.html', context)