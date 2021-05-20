from django.contrib import admin
from .models import Test, Choice, ChoiceTag

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

