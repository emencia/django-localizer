# -*- coding: UTF-8 -*-
#
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# Import from Django
from django.conf.urls import patterns
from django.contrib import admin
from django.contrib.admin import ModelAdmin, SimpleListFilter
from django.utils.translation import ugettext_lazy as _

# Import from Django-Localizer
from models import Message
from views import SyncMessages


class TranslatedFilter(SimpleListFilter):

    title = _('Translated')
    parameter_name = 'translated'

    def lookups(self, request, model_admin):
        return [
            ('translated', _('Translated')),
            ('not-translated', _('Not yet translated'))]

    def queryset(self, request, queryset):
        if self.value() == 'translated':
            return queryset.exclude(translation='')
        if self.value() == 'not-translated':
            return queryset.filter(translation='')


class MessageAdmin(ModelAdmin):

    # Table display
    list_display = ('msgid', 'language', 'msgstr', 'translation')
    list_filter = ['language', TranslatedFilter]
    search_fields = ('msgid', 'msgstr')

    # Edit form
    fields = ('msgid', 'language', 'msgstr', 'translation')
    readonly_fields = ('msgid', 'language', 'msgstr')

    # Tools
    change_list_template = 'localizer/message/change_list.html'

    def get_urls(self):
        urls = super(MessageAdmin, self).get_urls()
        urls = urls + patterns('',
            (r'^sync_messages$', SyncMessages.as_view()))
        return urls


admin.site.register(Message, MessageAdmin)
