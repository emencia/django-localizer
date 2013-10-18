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
