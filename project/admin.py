from django.contrib import admin
from .models import Test, Choice, ChoiceTag, Email, MenuItem
from django.urls import path
from django.http import HttpResponseRedirect
from django.contrib.auth.models import Permission
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
        email.send()
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    def send_to_user(self, request, object_id):
        email = Email.objects.get(id=object_id)
        
        if request.POST:
            
            file = request.FILES.get('distfile')
            if file:
                
                decoded_file = file.read().decode('utf-8').splitlines()
                reader = csv.DictReader(decoded_file)

                for row in reader:
                    for key, value in row.items():
                        if key.endswith('_LIST'):
                            row[key] = value.split(',')

                    email = Email.objects.get(id=object_id)

                    if request.POST.get('submit') == 'Upload CSV':  # Preview only
                        break

                    email.to = row['TO']
                    email.send()

            else:
                to = [s + '@umich.edu' for s in request.POST.get('to').split(',') ]
                cc = request.POST.get('cc').split(',')
                bcc = request.POST.get('bcc').split(',')

                if cc != ['']:
                    cc = [s + '@umich.edu' for s in cc ]

                if bcc != ['']:
                    bcc = [s + '@umich.edu' for s in bcc ]

                msg = EmailMultiAlternatives(email.subject, email.subject, email.sender, to, bcc=bcc, cc=cc)
                msg.attach_alternative(email.body, "text/html")
                msg.send()

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


class MenuItemInline(admin.TabularInline):
    model = MenuItem
    extra = 0
    show_change_link = True
    ordering = ("seq_num",)
    fields = (
        "code",
        "label",
        "seq_num",
        "active",
        "path",
        #"permissions"
    )
    readonly_fields = ("permissions",)
    #filter_horizontal = ("permissions",)

# --- MenuItem Admin (standalone editing) ---
@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ("label", "parent", "seq_num", "active", "path")
    search_fields = ("label",)
    inlines = [MenuItemInline]

    fieldsets = (
        (None, {
            "fields": (
                "code",
                "parent",
                ("active","seq_num","label","path"),
                "help_text",
            ),
        }),
        ("Permissions", {
            "classes": ("collapse",),
            "fields": ("permissions",),
        }),
    )

    filter_horizontal = ("permissions",)
    list_editable = ("seq_num", "active")

    ordering = ("seq_num",)

    change_list_template = "admin/project/menu/menu_preview.html",

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}

        qs = (
            self.get_queryset(request)
            .select_related("parent")
            .prefetch_related("permissions__content_type")
            .order_by("parent_id", "seq_num")
        )

        items = list(qs)

        # build tree (same logic as before)
        item_map = {item.code: item for item in items}
        for item in items:
            item.children_list = []

        roots = []
        for item in items:
            if item.parent_id and item.parent_id in item_map:
                item_map[item.parent_id].children_list.append(item)
            else:
                roots.append(item)

        extra_context["tree"] = roots

        return super().changelist_view(request, extra_context=extra_context)

    def formfield_for_manytomany(self, db_field, request, **kwargs):   # Fix N+1 issue when viewing permissions.
        if db_field.name == "permissions":
            kwargs["queryset"] = Permission.objects.select_related("content_type")
        return super().formfield_for_manytomany(db_field, request, **kwargs)


admin.site.register(Choice, ChoiceAdmin)
admin.site.register(DownloadLog)