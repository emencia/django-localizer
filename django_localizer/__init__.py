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
from django.utils.safestring import mark_safe, SafeData
from django.utils.translation import trans_real

# Import from Localizer
from models import Message


# Monkey patch
do_translate_old = trans_real.do_translate

def do_translate(msgid, translation_function):
    language = trans_real.get_language()
    # Normalize the message, like Django does
    is_safe = isinstance(msgid, SafeData)
    msgid = msgid.replace(str('\r\n'), str('\n')).replace(str('\r'), str('\n'))
    try:
        message = Message.objects.get(msgid=msgid, language=language)
    except Message.DoesNotExist:
        # Miss
        message = Message(msgid=msgid, language=language)
        message.save()
        msgstr = None
    else:
        # Hit
        msgstr = message.msgstr

    # Default
    if not msgstr:
        return do_translate_old(msgid, translation_function)

    return mark_safe(msgstr) if is_safe else msgstr


trans_real.do_translate = do_translate
