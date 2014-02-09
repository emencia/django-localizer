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
        from . import do_translate_old

        # Make a list with all the message ids in the source code
        keys = set()
        for catalog in trans_real._translations.values():
            for key in catalog._catalog.keys():
                if type(key) is unicode:
                    keys.add(key)
                elif type(key) is tuple:
                    pass # Plural forms not yet supported
                else:
                    raise TypeError, repr(key)

        # Remove empty messages
        Message.objects.filter(translation=u'').delete()

        # Make a list with all the messages missing in the database
        messages = []
        for language, title in settings.LANGUAGES:
            activate(language)
            for key in keys:
                try:
                    Message.objects.get(msgid=key, language=language)
                except Message.DoesNotExist:
                    msgstr = do_translate_old(key, 'ugettext')
                    message = Message(msgid=key, msgstr=msgstr,
                                      language=language)
                    messages.append(message)

        # Bulk create the messages
        Message.objects.bulk_create(messages)

        # Ok, go back
        return HttpResponseRedirect('.')
