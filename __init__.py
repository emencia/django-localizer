# -*- coding: UTF-8 -*-

from django.utils.translation import trans_real


# Monkey patch
do_translate_old = trans_real.do_translate

def do_translate(message, translation_function):
    language = trans_real.get_language()
    print "LOCALIZER:", message, language, translation_function
    return do_translate_old(message, translation_function)


trans_real.do_translate = do_translate
