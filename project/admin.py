from django.contrib import admin
from .models import Test, Choice, ChoiceTag, Email
from django.urls import path
from django.http import HttpResponseRedirect
from django.core.mail import send_mail
from django.core.management import call_command
from django.template.response import TemplateResponse
from django.core.mail import EmailMultiAlternatives
from reports.toll.models import DownloadLog
import csv

@admin.register(Email)
class EmailAdmin(admin.ModelAdmin):
    list_display = ['code','subject']

    def get_urls(self):
        urls = super().get_urls()

        download_url = [
            path('<int:object_id>/send_test/', self.send_test),
            path('<int:object_id>/send_to_user/', self.send_to_user),
        ]
        return download_url + urls

    def change_view(self, request, object_id, form_url='', extra_context=None):
        email = Email.objects.get(id=object_id)

        return super().change_view(
            request, object_id, form_url, extra_context={'email': email},
        )

    def send_test(self, request, object_id):
        email = Email.objects.get(id=object_id)

        call_command('softphone_email', email=email.code, audit=1)

        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    def send_to_user(self, request, object_id):
        email = Email.objects.get(id=object_id)
        
        if request.POST:
            
            if request.POST.get('submit') == 'Upload CSV':

                file = request.FILES['distfile'] 
                decoded_file = file.read().decode('utf-8').splitlines()
                reader = csv.DictReader(decoded_file)

                print('show preview')
                #ontext = {}
                context = next(reader)
                for key, value in context.items():
                    if key.endswith('_LIST'):
                        context[key] = value.split(',')

                email.update_body(context)
                email.send()

            #for row in reader:
            #    print(row)
                
            to = [s + '@umich.edu' for s in request.POST.get('to').split(',') ]
            cc = request.POST.get('cc').split(',')
            bcc = request.POST.get('bcc').split(',')

            if cc != ['']:
                cc = [s + '@umich.edu' for s in cc ]

            if bcc != ['']:
                bcc = [s + '@umich.edu' for s in bcc ]

            #msg = EmailMultiAlternatives(email.subject, email.subject, email.sender, to, bcc=bcc, cc=cc)
            #msg.attach_alternative(email.body, "text/html")
            #msg.send()

        return TemplateResponse(
            request,
            'admin/project/email/ad_hoc.html',
            {
            'opts': self.opts,
            'email': email,
            }
        )


class TestAdmin(admin.ModelAdmin):
    list_display = ('user','url','result')
    ordering = ('user','url')
    search_fields = ('url',)

admin.site.register(Test, TestAdmin)


class ChoiceInline(admin.TabularInline):
    model = Choice
    fk_name = 'parent'

class ChoiceAdmin(admin.ModelAdmin):
    list_display = ('code','sequence','label','parent')
    ordering = ('parent','sequence')
    search_fields = ('parent',)

    inlines = [
        ChoiceInline,
    ]

admin.site.register(Choice, ChoiceAdmin)
admin.site.register(DownloadLog)
