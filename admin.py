# -*- coding: UTF-8 -*-

# Import from Django
from django.contrib import admin
from django.contrib.admin import ModelAdmin

# Import from Localizer
from models import Message


class MessageAdmin(ModelAdmin):
    fields = ('msgid', 'language', 'msgstr')
    readonly_fields = ('msgid', 'language')

    list_display = ('msgid', 'language', 'msgstr')
    list_filter = ('language',)
    search_fields = ('msgid', 'msgstr')

    def has_add_permission(self, request):
        return False


admin.site.register(Message, MessageAdmin)
