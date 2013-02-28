# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'ScheduleRule.days_of_week'
        db.add_column('schedule_schedulerule', 'days_of_week',
                      self.gf('schedule.fields.DaysOfWeekField')(default=0),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'ScheduleRule.days_of_week'
        db.delete_column('schedule_schedulerule', 'days_of_week')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'design.choretype': {
            'Meta': {'object_name': 'ChoreType'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'owners': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['hr.Organization']"}),
            'traits_forbidden': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'chores_forbidding_trait'", 'blank': 'True', 'to': "orm['hr.Trait']"}),
            'traits_required': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'chores_requiring_trait'", 'blank': 'True', 'to': "orm['hr.Trait']"})
        },
        'hr.body': {
            'Meta': {'object_name': 'Body'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['hr.Organization']", 'null': 'True', 'blank': 'True'})
        },
        'hr.organization': {
            'Meta': {'object_name': 'Organization', '_ormbases': ['hr.Body']},
            'body_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['hr.Body']", 'unique': 'True', 'primary_key': 'True'}),
            'managers': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['auth.Group']", 'unique': 'True'})
        },
        'hr.trait': {
            'Meta': {'object_name': 'Trait'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'schedule.schedulerule': {
            'Meta': {'object_name': 'ScheduleRule'},
            'chore': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['design.ChoreType']"}),
            'days': ('django.db.models.fields.IntegerField', [], {}),
            'days_of_week': ('schedule.fields.DaysOfWeekField', [], {}),
            'end_date': ('django.db.models.fields.DateField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'quantity': ('django.db.models.fields.IntegerField', [], {}),
            'start_date': ('django.db.models.fields.DateField', [], {})
        }
    }

    complete_apps = ['schedule']