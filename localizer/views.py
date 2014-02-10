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


class SyncMessages(TemplateView):
    template_name = 'localizer/message/sync_messages.html'

    def post(self, request, *args, **kw):
        paths = get_paths_to_po_files()

        # Read the PO files
        source = {}
        for language, title in settings.LANGUAGES:
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

        # Remove empty messages
        Message.objects.filter(translation=u'').delete()

        # Make a list with all the messages missing in the database
        messages = []
        for language, title in settings.LANGUAGES:
            for key in source:
                msgstr = source[key].get(language, u'')
                msgid, plural = key
                kw = {'msgid': msgid, 'plural': plural, 'language': language}
                try:
                    message = Message.objects.get(**kw)
                except Message.DoesNotExist:
                    kw['msgstr'] = msgstr
                    message = Message(**kw)
                    messages.append(message)

        # Bulk create the messages
        Message.objects.bulk_create(messages)

        # Ok, go back
        return HttpResponseRedirect('.')
