# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'ChoreType'
        db.create_table('design_choretype', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('owners', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['hr.Organization'])),
        ))
        db.send_create_signal('design', ['ChoreType'])

        # Adding M2M table for field traits_required on 'ChoreType'
        db.create_table('design_choretype_traits_required', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('choretype', models.ForeignKey(orm['design.choretype'], null=False)),
            ('trait', models.ForeignKey(orm['hr.trait'], null=False))
        ))
        db.create_unique('design_choretype_traits_required', ['choretype_id', 'trait_id'])

        # Adding M2M table for field traits_forbidden on 'ChoreType'
        db.create_table('design_choretype_traits_forbidden', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('choretype', models.ForeignKey(orm['design.choretype'], null=False)),
            ('trait', models.ForeignKey(orm['hr.trait'], null=False))
        ))
        db.create_unique('design_choretype_traits_forbidden', ['choretype_id', 'trait_id'])


    def backwards(self, orm):
        # Deleting model 'ChoreType'
        db.delete_table('design_choretype')

        # Removing M2M table for field traits_required on 'ChoreType'
        db.delete_table('design_choretype_traits_required')

        # Removing M2M table for field traits_forbidden on 'ChoreType'
        db.delete_table('design_choretype_traits_forbidden')


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
            'traits_forbidden': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'chores_forbidding_trait'", 'symmetrical': 'False', 'to': "orm['hr.Trait']"}),
            'traits_required': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'chores_requiring_trait'", 'symmetrical': 'False', 'to': "orm['hr.Trait']"})
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
        }
    }

    complete_apps = ['design']