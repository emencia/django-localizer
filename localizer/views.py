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
from os.path import basename, dirname, isdir, isfile, join as join_path

# Import from Django
from django import http
from django.conf import settings
from django.http import HttpResponseRedirect
from django.views.generic import TemplateView
from django.utils import six
from django.utils.text import javascript_quote
from django.utils.translation import (check_for_language, activate, to_locale,
                                      get_language)

from django.views.i18n import (LibHead, SimplePlural, PluralIdx,
                               LibFoot, InterPolate, LibFormatHead,
                               get_formats, LibFormatFoot)

# Import from polib
from polib import pofile

# Import from Django-Localizer
from models import Message

_DOMAINS = ["django.po", "djangojs.po"]


def get_paths_to_po_files():
    paths = []
    for appname in reversed(settings.INSTALLED_APPS):
        app = import_module(appname)
        path = join_path(dirname(app.__file__), 'locale')
        paths.append(path)

    for path in reversed(settings.LOCALE_PATHS):
        paths.append(path)

    return [x + '/%s/LC_MESSAGES/{}'.format(domain)
            for x in paths if isdir(x)
            for domain in _DOMAINS]


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
        languages = [x[0] for x in settings.LANGUAGES]

        # Read the PO files
        source = {}
        for language in languages:
            for path in paths:
                domain = basename(path)[:-3]
                path = path % language
                if not isfile(path):
                    continue
                po = pofile(path)
                for entry in po:
                    msgid = entry.msgid
                    if entry.msgstr_plural:
                        for plural, msgstr in entry.msgstr_plural.items():
                            key = (msgid, int(plural), domain)
                            source.setdefault(key, {})[language] = msgstr
                    else:
                        key = (msgid, None, domain)
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
            key = (message.msgid, message.plural, message.domain)
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
            msgid, plural, domain = key
            for language, msgstr in value.items():
                message = Message(msgid=msgid, plural=plural,
                                  language=language, msgstr=msgstr,
                                  domain=domain)
                messages.append(message)

        # Bulk create the messages
        Message.objects.bulk_create(messages)

        # Ok, go back
        return HttpResponseRedirect('.')


def javascript_catalog(request, domain='djangojs', packages=None):
    """
    Returns the selected language catalog as a javascript library.

    Receives the list of packages to check for translations in the
    packages parameter either from an infodict or as a +-delimited
    string from the request. Default is 'django.conf'.

    Additionally you can override the gettext domain for this view,
    but usually you don't want to do that, as JavaScript messages
    go to the djangojs domain. But this might be needed if you
    deliver your JavaScript source from Django templates.
    """
    # (TODO): cache dictionary
    if request.GET:
        if 'language' in request.GET:
            if check_for_language(request.GET['language']):
                activate(request.GET['language'])
    if packages is None:
        packages = ['django.conf']
    if isinstance(packages, six.string_types):
        packages = packages.split('+')
    packages = [p for p in packages if p ==
                'django.conf' or p in settings.INSTALLED_APPS]
    locale = to_locale(get_language())
    t = {}

    # Singular forms
    aux_catalog = Message.objects.filter(
        domain=domain, plural__isnull=True, language=locale).values_list(
        "msgid", "msgstr", "translation")

    for message in aux_catalog:
        # Case there is translation
        if len(message[2]):
            aux_message = {message[0]: message[2]}
        # Case no translation but .po msgstr translation
        elif len(message[1]):
            aux_message = {message[0]: message[1]}
        # Case no translations
        else:
            aux_message = {message[0]: message[0]}

        t.update(aux_message)

    # Plural forms (TODO)
    # plural_msgs = dict(Message.objects.filter(
    #     domain=domain, plural__isnull=False).values_list(
    #     "msgid", "translation"))

    src = [LibHead]
    plural = None
    if '' in t:
        for l in t[''].split('\n'):
            if l.startswith('Plural-Forms:'):
                plural = l.split(':', 1)[1].strip()
    if plural is not None:
        # this should actually be a compiled function of a typical plural-form:
        # Plural-Forms: nplurals=3; plural=n%10==1 && n%100!=11 ? 0 : n%10>=2
        # && n%10<=4 && (n%100<10 || n%100>=20) ? 1 : 2;
        plural = [el.strip() for el in plural.split(
            ';') if el.strip().startswith('plural=')][0].split('=', 1)[1]
        src.append(PluralIdx % plural)
    else:
        src.append(SimplePlural)
    csrc = []
    pdict = {}

    for k, v in t.items():
        if k == '':
            continue
        if isinstance(k, six.string_types):
            if len(v) == 0:
                csrc.append("catalog['%s'] = '%s';\n" %
                            (javascript_quote(k), javascript_quote(k)))
            else:
                csrc.append("catalog['%s'] = '%s';\n" %
                            (javascript_quote(k), javascript_quote(v)))
        elif isinstance(k, tuple):
            if k[0] not in pdict:
                pdict[k[0]] = k[1]
            else:
                pdict[k[0]] = max(k[1], pdict[k[0]])
            csrc.append("catalog['%s'][%d] = '%s';\n" % (
                javascript_quote(k[0]), k[1], javascript_quote(v)))
        else:
            raise TypeError(k)
    csrc.sort()
    for k, v in pdict.items():
        src.append("catalog['%s'] = [%s];\n" %
                   (javascript_quote(k), ','.join(["''"] * (v + 1))))
    src.extend(csrc)
    src.append(LibFoot)
    src.append(InterPolate)
    src.append(LibFormatHead)
    src.append(get_formats())
    src.append(LibFormatFoot)
    src = ''.join(src)
    return http.HttpResponse(src, 'text/javascript')
