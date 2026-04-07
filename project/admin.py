from django.contrib import admin
from .models import Test, Choice, ChoiceTag, Email, ChoiceSet
from django.urls import path, reverse
from django.http import HttpResponseRedirect
from django.db.models import Q, Count
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
    list_display = ("code", "sequence", "label", "parent")

    def get_urls(self):
        urls = super().get_urls()
        custom = [
            path(
                "dashboard/",
                self.admin_site.admin_view(self.dashboard_view),
                name="project_choice_dashboard",
            ),
        ]
        return custom + urls


    def dashboard_view(self, request):
        from django.db.models import Q, Count
        from django.urls import reverse

        q = (request.GET.get("q") or "").strip()

        # Base querysets
        all_choices = Choice.objects.all()
        tags_qs = ChoiceTag.objects.all()

        # Treat "root" choices as your "sets" (parent is null)
        roots = all_choices.filter(parent__isnull=True)

        # Search (adjust fields if you want more)
        if q:
            all_choices = all_choices.filter(Q(code__icontains=q) | Q(label__icontains=q))
            roots = roots.filter(Q(code__icontains=q) | Q(label__icontains=q))

        # Stats (your model uses `active`, not `is_active`)
        stats = {
            "choice_sets": roots.count(),
            "options": all_choices.count(),
            "tags": tags_qs.count(),
            "inactive": Choice.objects.filter(active=False).count(),
        }

        # Count children (your reverse name appears to be `choice`, not `children`)
        # If you later rename related_name to "children", change Count("choice") -> Count("children")
        roots = roots.annotate(option_count=Count("choice")).order_by("code")

        # Admin URLs
        changelist_url = reverse("admin:project_choice_changelist")
        change_url_name = "admin:project_choice_change"

        choice_sets = []
        for r in roots:
            choice_sets.append(
                {
                    "code": r.code,
                    "label": r.label,
                    "is_active": r.active,
                    "option_count": r.option_count,
                    # link to the Choice changelist filtered to children of this root
                    "admin_url": f"{changelist_url}?parent__id__exact={r.id}",
                }
            )

        recent_qs = Choice.objects.order_by("-id")[:10]
        recent_options = []
        for opt in recent_qs:
            recent_options.append(
                {
                    "key": opt.code,
                    "label": opt.label,
                    "admin_url": reverse(change_url_name, args=[opt.id]),
                }
            )

        # Basic health checks
        # (If FK integrity is enforced, orphans should be 0. Still useful if legacy DB edits happen.)
        orphans = Choice.objects.filter(parent_id__isnull=False, parent__isnull=True).count()

        duplicates = (
            Choice.objects.values("code")
            .annotate(n=Count("id"))
            .filter(n__gt=1)
            .count()
        )

        health = {
            "orphans": orphans,
            "duplicates": duplicates,
            "cycles": "—",
            "status": "ok" if (orphans == 0 and duplicates == 0) else "warn",
        }

        context = {
            **self.admin_site.each_context(request),
            "q": q,
            "stats": stats,
            "choice_sets": choice_sets,
            "recent_options": recent_options,
            "health": health,
        }

        return TemplateResponse(request, "admin/choices/dashboard.html", context)



admin.site.register(Choice, ChoiceAdmin)
admin.site.register(DownloadLog)
