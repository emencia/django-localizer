# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Removing unique constraint on 'Message', fields ['msgid', 'language']
        db.delete_unique(u'localizer_message', ['msgid', 'language'])

        # Adding field 'Message.plural'
        db.add_column(u'localizer_message', 'plural',
                      self.gf('django.db.models.fields.IntegerField')(null=True),
                      keep_default=False)

        # Adding unique constraint on 'Message', fields ['msgid', 'plural', 'language']
        db.create_unique(u'localizer_message', ['msgid', 'plural', 'language'])


    def backwards(self, orm):
        # Removing unique constraint on 'Message', fields ['msgid', 'plural', 'language']
        db.delete_unique(u'localizer_message', ['msgid', 'plural', 'language'])

        # Deleting field 'Message.plural'
        db.delete_column(u'localizer_message', 'plural')

        # Adding unique constraint on 'Message', fields ['msgid', 'language']
        db.create_unique(u'localizer_message', ['msgid', 'language'])


    models = {
        u'localizer.message': {
            'Meta': {'unique_together': "(('msgid', 'plural', 'language'),)", 'object_name': 'Message'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'msgid': ('django.db.models.fields.TextField', [], {}),
            'msgstr': ('django.db.models.fields.TextField', [], {}),
            'plural': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'translation': ('django.db.models.fields.TextField', [], {'blank': 'True'})
        }
    }

    complete_apps = ['localizer']