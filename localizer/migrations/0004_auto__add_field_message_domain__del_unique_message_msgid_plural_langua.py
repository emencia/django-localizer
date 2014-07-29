# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Removing unique constraint on 'Message', fields ['msgid', 'plural', 'language']
        db.delete_unique(u'localizer_message', ['msgid', 'plural', 'language'])

        # Adding field 'Message.domain'
        db.add_column(u'localizer_message', 'domain',
                      self.gf('django.db.models.fields.CharField')(default='django', max_length=30),
                      keep_default=False)

        # Adding unique constraint on 'Message', fields ['msgid', 'plural', 'language', 'domain']
        db.create_unique(u'localizer_message', ['msgid', 'plural', 'language', 'domain'])


    def backwards(self, orm):
        # Removing unique constraint on 'Message', fields ['msgid', 'plural', 'language', 'domain']
        db.delete_unique(u'localizer_message', ['msgid', 'plural', 'language', 'domain'])

        # Deleting field 'Message.domain'
        db.delete_column(u'localizer_message', 'domain')

        # Adding unique constraint on 'Message', fields ['msgid', 'plural', 'language']
        db.create_unique(u'localizer_message', ['msgid', 'plural', 'language'])


    models = {
        u'localizer.message': {
            'Meta': {'unique_together': "(('msgid', 'plural', 'language', 'domain'),)", 'object_name': 'Message'},
            'domain': ('django.db.models.fields.CharField', [], {'default': "'django'", 'max_length': '30'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'msgid': ('django.db.models.fields.TextField', [], {}),
            'msgstr': ('django.db.models.fields.TextField', [], {}),
            'plural': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'stale': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'translation': ('django.db.models.fields.TextField', [], {'blank': 'True'})
        }
    }

    complete_apps = ['localizer']