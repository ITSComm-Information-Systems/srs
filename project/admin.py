from django.contrib import admin
from .models import Test, Choice, ChoiceTag, Email
from django.urls import path
from django.http import HttpResponseRedirect
from django.core.mail import send_mail

@admin.register(Email)
class EmailAdmin(admin.ModelAdmin):

    def get_urls(self):
        urls = super().get_urls()

        download_url = [
            path('<int:object_id>/send_email/', self.send_email),
        ]
        return download_url + urls

    def send_email(self, request, object_id):
        email = Email.objects.get(id=object_id)

        send_mail(
            email.subject,
            'See attachment.',
            email.sender,
            [request.user.email],
            fail_silently=False,
            html_message=email.body
        )

        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


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

