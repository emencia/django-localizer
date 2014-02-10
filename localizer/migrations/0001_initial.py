# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Message'
        db.create_table(u'localizer_message', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('msgid', self.gf('django.db.models.fields.TextField')()),
            ('language', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('msgstr', self.gf('django.db.models.fields.TextField')()),
            ('translation', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal(u'localizer', ['Message'])

        # Adding unique constraint on 'Message', fields ['msgid', 'language']
        db.create_unique(u'localizer_message', ['msgid', 'language'])


    def backwards(self, orm):
        # Removing unique constraint on 'Message', fields ['msgid', 'language']
        db.delete_unique(u'localizer_message', ['msgid', 'language'])

        # Deleting model 'Message'
        db.delete_table(u'localizer_message')


    models = {
        u'localizer.message': {
            'Meta': {'unique_together': "(('msgid', 'language'),)", 'object_name': 'Message'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'msgid': ('django.db.models.fields.TextField', [], {}),
            'msgstr': ('django.db.models.fields.TextField', [], {}),
            'translation': ('django.db.models.fields.TextField', [], {'blank': 'True'})
        }
    }

    complete_apps = ['localizer']