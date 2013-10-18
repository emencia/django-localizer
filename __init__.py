# -*- coding: UTF-8 -*-

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
