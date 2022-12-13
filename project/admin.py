from django.contrib import admin
from .models import Test, Choice, ChoiceTag, Email
from django.urls import path
from django.http import HttpResponseRedirect
from django.template.response import TemplateResponse
from django.core.mail import send_mail
from django.core.management import call_command

@admin.register(Email)
class EmailAdmin(admin.ModelAdmin):
    list_display = ['code','subject']

    def get_urls(self):
        urls = super().get_urls()

        download_url = [
            path('<int:object_id>/send_email/', self.send_email),
            path('<int:object_id>/send_to_list/', self.send_to_list),
        ]
        return download_url + urls

    def change_view(self, request, object_id, form_url='', extra_context=None):
        email = Email.objects.get(id=object_id)

        return super().change_view(
            request, object_id, form_url, extra_context={'email': email},
        )

    def send_email(self, request, object_id):
        email = Email.objects.get(id=object_id)

        call_command('softphone_email', email=email.code, audit=1)

        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    def send_to_list(self, request, object_id):
        email = Email.objects.get(id=object_id)

        if request.method == 'POST':
            recipients = request.POST.get('recipents')
            call_command('softphone_email', email=email.code, userlist=recipients)

        return TemplateResponse(
            request,
            'admin/project/email/send_to_list.html',
            {
            'email': email,
            'opts': self.opts
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

