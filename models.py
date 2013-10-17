# -*- coding: UTF-8 -*-

# Import
from django.db.models import Model
from django.db.models import CharField, TextField


class Message(Model):

    msgid = TextField()
    msgstr = TextField()
    language = CharField(max_length=20)

    class Meta:
        unique_together = ('msgid', 'language')
