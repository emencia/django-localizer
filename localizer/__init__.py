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

# Import from the future
from __future__ import unicode_literals

# Import from Django
from django.db import connection
from django.utils.safestring import mark_safe, SafeData
from django.utils.translation import trans_real

# Import from Localizer
from models import Message


# Monkey patch
do_translate_old = trans_real.do_translate
do_ntranslate_old = trans_real.do_ntranslate


def do_translate(msgid, translation_function):
    language = trans_real.get_language()
    # Normalize the message, like Django does
    is_safe = isinstance(msgid, SafeData)
    msgid = msgid.replace(str('\r\n'), str('\n')).replace(str('\r'), str('\n'))

    kw = {'msgid': msgid, 'language': language}
    try:
        message = Message.objects.get(**kw)
    except Message.DoesNotExist:
        # Miss
        msgstr = do_translate_old(msgid, translation_function)
        kw['msgstr'] = msgstr
        message = Message(**kw)
        message.save()
        return msgstr

    # Hit
    translation = message.translation
    if not translation:
        return do_translate_old(msgid, translation_function)

    return mark_safe(translation) if is_safe else translation


def do_ntranslate(singular, plural, number, translation_function):
    language = trans_real.get_language()

    translation = trans_real.translation(language)
    number = translation.plural(number)

    kw = {'msgid': singular, 'plural': number, 'language': language}
    try:
        message = Message.objects.get(**kw)
    except Message.DoesNotExist:
        # Miss
        msgstr = do_ntranslate_old(singular, plural, number,
                                   translation_function)
        kw['msgstr'] = msgstr
        message = Message(**kw)
        message.save()
        return msgstr

    # Hit
    translation = message.translation
    if not translation:
        return do_ntranslate_old(singular, plural, number,
                                 translation_function)

    return translation


# Enable translation only if the tables are there
# (otherwise syncdb fails)
if 'localizer_message' in connection.introspection.table_names():
    trans_real.do_translate = do_translate
    trans_real.do_ntranslate = do_ntranslate
