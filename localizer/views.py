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

# Import from the Standard Library
from importlib import import_module
from os.path import dirname, isdir, isfile, join as join_path

# Import from Django
from django.conf import settings
from django.http import HttpResponseRedirect
from django.views.generic import TemplateView

# Import from polib
from polib import pofile

# Import from Django-Localizer
from models import Message


def get_paths_to_po_files():
    paths = []
    for appname in reversed(settings.INSTALLED_APPS):
        app = import_module(appname)
        path = join_path(dirname(app.__file__), 'locale')
        paths.append(path)

    for path in reversed(settings.LOCALE_PATHS):
        paths.append(path)

    return [ x + '/%s/LC_MESSAGES/django.po' for x in paths if isdir(x) ]


def delete_message(message):
    # Delete only if empty
    if message.translation:
        message.msgstr = u''
        message.stale = True
        message.save()
    else:
        message.delete()


class SyncMessages(TemplateView):
    template_name = 'localizer/message/sync_messages.html'

    def post(self, request, *args, **kw):
        paths = get_paths_to_po_files()
        languages = [ x[0] for x in settings.LANGUAGES ]

        # Read the PO files
        source = {}
        for language in languages:
            for path in paths:
                path = path % language
                if not isfile(path):
                    continue
                po = pofile(path)
                for entry in po:
                    msgid = entry.msgid
                    if entry.msgstr_plural:
                        for plural, msgstr in entry.msgstr_plural.items():
                            key = (msgid, int(plural))
                            source.setdefault(key, {})[language] = msgstr
                    else:
                        key = (msgid, None)
                        source.setdefault(key, {})[language] = entry.msgstr

        # Fill source for missing translations, so it is complete
        for value in source.values():
            for language in languages:
                value.setdefault(language, u'')

        # Delete or update
        for message in Message.objects.all():
            # Case 1: language not supported anymore
            if message.language not in languages:
                delete_message(message)
                continue

            # Case 2: message not in the source anymore
            key = (message.msgid, message.plural)
            value = source.get(key)
            if value is None:
                delete_message(message)
                continue

            # Case 3: update
            msgstr = value.pop(message.language)
            if message.msgstr != msgstr or message.stale is not False:
                message.msgstr = msgstr
                message.stale = False
                message.save()

            # Clean
            if not value:
                del source[key]

        # Make a list with all the messages missing in the database
        messages = []
        for key, value in source.items():
            msgid, plural = key
            for language, msgstr in value.items():
                message = Message(msgid=msgid, plural=plural,
                                  language=language, msgstr=msgstr)
                messages.append(message)

        # Bulk create the messages
        Message.objects.bulk_create(messages)

        # Ok, go back
        return HttpResponseRedirect('.')
