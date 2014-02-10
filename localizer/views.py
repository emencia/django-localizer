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
from django.conf import settings
from django.http import HttpResponseRedirect
from django.utils.translation import activate
from django.utils.translation import trans_real
from django.views.generic import TemplateView

# Import from Django-Localizer
from models import Message



class SyncMessages(TemplateView):
    template_name = 'localizer/message/sync_messages.html'

    def post(self, request, *args, **kw):
        # Make a dict with all the messages in the source code
        # TODO Empty messages are not in the MO files
        source = {}
        for language, catalog in trans_real._translations.items():
            for key, value in catalog._catalog.items():
                source.setdefault(key, {})[language] = value

        # Remove empty messages
        Message.objects.filter(translation=u'').delete()

        # Make a list with all the messages missing in the database
        messages = []
        for language, title in settings.LANGUAGES:
            activate(language)
            for key in source:
                value = source[key].get(language, u'')
                if type(key) is unicode:
                    kw = {'msgid': key}
                elif type(key) is tuple:
                    kw = {'msgid': key[0], 'plural': key[1]}
                else:
                    raise TypeError, repr(key)

                kw['language'] = language

                try:
                    message = Message.objects.get(**kw)
                except Message.DoesNotExist:
                    kw['msgstr'] = value
                    message = Message(**kw)
                    messages.append(message)

        # Bulk create the messages
        Message.objects.bulk_create(messages)

        # Ok, go back
        return HttpResponseRedirect('.')
