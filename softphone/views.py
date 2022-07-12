from django.http import HttpResponseRedirect 
from django.shortcuts import redirect, render
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import View
from django.core.paginator import Paginator

from django.forms import formset_factory
from oscauth.models import AuthUserDept, AuthUserDeptV
from project.pinnmodels import UmOscDeptProfileV
from project.models import Choice
from project.utils import download_csv_from_queryset
from pages.models import Page
from .models import SubscriberCharges, Selection, SelectionV, DeptV
from .forms import SelectionForm
from django.contrib.auth.decorators import login_required, permission_required


def get_help(request):

    return render(request, 'softphone/help.html',
                        {'title': 'Softphone Help',
                        'context': 	Page.objects.filter(permalink='/SFMainHelp').first()})    


@login_required
def landing_page(request):
    user_dept_list = list(AuthUserDeptV.objects.filter(user_id=request.user.id,codename='can_report').values_list('dept', flat=True))
    dept_list = DeptV.objects.filter(dept_id__in=user_dept_list)

    return render(request, 'softphone/home.html',
                        {'title': 'Telephone Audit',
                        'notices': 	Page.objects.get(permalink='/SFSideBar')
                        ,'dept_list': dept_list})

def get_department_list(dept_id, user):
    user_dept_list = list(AuthUserDeptV.objects.filter(user_id=user.id,codename='can_report').values_list('dept', flat=True))
    dept_list = DeptV.objects.filter(dept_id__in=user_dept_list)


    current_department = str(dept_id)
    found = False

    for dept in dept_list:
        if dept.dept_id == current_department:
            dept.selected = 'selected'
            found = True
            break
    
    if not found:
        dept_list.access_error = f'NO ACCESS TO {current_department}'

    return dept_list

class StepSubscribers(LoginRequiredMixin, View):

    def post(self, request, dept_id):
        target_page = request.POST.get('target_page')
        target_card = request.POST.get('target_card','')

        subscribers = self.request.POST.getlist('subscriber')
        page = request.GET.get('page', 1)

        selections = request.session.get('softphone_selection')
        if not selections:
            request.session['softphone_selection'] = {}

        request.session['softphone_selection'].update({page: subscribers})
        request.session['softphone_page'] = request.GET.get('page', 1)

        if target_page:
            return HttpResponseRedirect(f'?page={ target_page }{target_card}')   
        else:
            return HttpResponseRedirect('details/')

    def get(self, request, dept_id):
        if not request.GET.get('page'):
            request.session['softphone_selection'] = {}

        page_number = request.GET.get('page', 1)
        full_list = Selection.objects.with_charges(dept_id=dept_id)

        paginator = Paginator(full_list, 50)
        phone_list = paginator.page(page_number)

        dept_list = get_department_list(dept_id, request.user)
        if hasattr(dept_list, 'access_error'):
            if not request.user.is_superuser:
                return render(request, 'softphone/step_subscribers.html',
                        {'title': 'Softphone',
                        'dept_list': dept_list,
                        'dept_id': dept_id})

        cards_selected = 0
        selections = request.session.get('softphone_selection')
        if selections:
            for key, value in selections.items():
                if key == page_number:   # Mark selections for current page
                    for phone in phone_list:
                        if phone['subscriber'] in value:
                            phone['checked'] ='checked'
                else:
                    cards_selected = cards_selected + len(value)

        return render(request, 'softphone/step_subscribers.html',
                      {'title': 'Softphone',
                       'selections_made': Selection.objects.selections_made(dept_id=dept_id),
                       'cards_selected': cards_selected,
                       'phone_list': phone_list,
                       'full_list': full_list,
                       'dept_list': dept_list,
                       'dept_id': dept_id})


class StepDetails(View):

    def get(self, request, dept_id):

        phones_selected = set()
        for page in request.session['softphone_selection'].values():
            phones_selected.update(page)

        page = request.session['softphone_page']
        phone_list = Selection.objects.with_charges(dept_id=dept_id, subscribers=phones_selected)

        SelectionFormSet = formset_factory(SelectionForm, extra=0)
        selection_formset = SelectionFormSet(initial=phone_list)

        return render(request, 'softphone/step_details.html',
                      {'title': 'Softphone',
                       'selection_formset': selection_formset,
                       'selections_made': Selection.objects.selections_made(dept_id=dept_id),
                       'phone_list': phone_list,
                       'page': page,
                       'dept_id': dept_id})

    def post(self, request, dept_id):

        phones_selected = []
        for key, value in self.request.POST.items():  # Deal with deleted forms
            if key.endswith('subscriber'):
                phones_selected.append(value)

        target_page = self.request.POST.get('target_page')
        if target_page:  # Back Button - clear removed selections
            for page, subs in request.session['softphone_selection'].items():
                for subscriber in subs:
                    if subscriber not in phones_selected:
                        request.session['softphone_selection'][page].remove(subscriber)
                        request.session.modified = True       

            return HttpResponseRedirect(target_page)


        page = request.session.get('softphone_page')
        phone_list = Selection.objects.with_charges(dept_id=dept_id, subscribers=phones_selected)

        SelectionFormSet = formset_factory(SelectionForm, extra=0)
        selection_formset = SelectionFormSet(request.POST, initial=phone_list)

        selections_errored = 0
        selections_saved = 0

        if selection_formset.is_valid():
            for form in selection_formset:
                form.save(request.user.username)

            request.session['softphone_selection'] = {}
            return HttpResponseRedirect(f'/softphone/dept/{dept_id}/confirmation/')
        else:
            print('invalid', selection_formset.errors)

        return render(request, 'softphone/step_details.html',
                    {'title': 'Softphone',
                    'selection_formset': selection_formset,
                    'selections_made': Selection.objects.selections_made(dept_id=dept_id),
                    'selections_saved': selections_saved,
                    'selections_errored': selections_errored,
                    'phone_list': phone_list,
                    'page': page,
                    'dept_id': dept_id})


class StepConfirmation(View):

    def get(self, request, dept_id):

        return render(request, 'softphone/step_confirmation.html',
                      {'title': 'Softphone',
                       'dept_id': dept_id})


class Selections(View):

    def get(self, request, dept_id):
        
        selection_list = SelectionV.objects.filter(dept_id=dept_id).order_by('-update_date','service_number')
        dept_list = get_department_list(dept_id, request.user)

        choice_list = {}

        for choice in Choice.objects.filter(parent__code='SOFTPHONE_MIGRATE'):
            choice_list[choice.code] = choice.label

        for selection in selection_list:
            selection.convert = choice_list.get(selection.migrate, '')


        return render(request, 'softphone/selections.html',
                      {'title': 'Softphone',
                       'selection_list': selection_list,
                       'dept_list': dept_list,
                       'dept_id': dept_id})


def download_csv(request, dept_id):
    qs = SelectionV.objects.filter(dept_id='481091').order_by('-update_date','service_number')
    #qs = Selection.
    return download_csv_from_queryset(qs)
