# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Message.stale'
        db.add_column(u'localizer_message', 'stale',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Message.stale'
        db.delete_column(u'localizer_message', 'stale')


    models = {
        u'localizer.message': {
            'Meta': {'unique_together': "(('msgid', 'plural', 'language'),)", 'object_name': 'Message'},
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