# osc\pages\view 
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseRedirect
from django.conf import settings
from django.contrib.auth.decorators import login_required

from . models import Page

@login_required
def index(request, pagename):
    pagename = '/' + pagename
    pg = get_object_or_404(Page, permalink=pagename)

    if not request.user.is_authenticated and pg.permalink == '/help':
        # make user login so we can get username for email
        return redirect('%s?next=%s' % (settings.LOGIN_URL, request.path))

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
