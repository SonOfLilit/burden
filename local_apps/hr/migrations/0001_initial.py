# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Trait'
        db.create_table('hr_trait', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
        ))
        db.send_create_signal('hr', ['Trait'])

        # Adding model 'Body'
        db.create_table('hr_body', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('parent', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['hr.Organization'], null=True, blank=True)),
        ))
        db.send_create_signal('hr', ['Body'])

        # Adding model 'Organization'
        db.create_table('hr_organization', (
            ('body_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['hr.Body'], unique=True, primary_key=True)),
            ('managers', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['auth.Group'], unique=True)),
        ))
        db.send_create_signal('hr', ['Organization'])

        # Adding model 'Worker'
        db.create_table('hr_worker', (
            ('body_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['hr.Body'], unique=True, primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['auth.User'], unique=True)),
        ))
        db.send_create_signal('hr', ['Worker'])

        # Adding M2M table for field traits on 'Worker'
        db.create_table('hr_worker_traits', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('worker', models.ForeignKey(orm['hr.worker'], null=False)),
            ('trait', models.ForeignKey(orm['hr.trait'], null=False))
        ))
        db.create_unique('hr_worker_traits', ['worker_id', 'trait_id'])


    def backwards(self, orm):
        # Deleting model 'Trait'
        db.delete_table('hr_trait')

        # Deleting model 'Body'
        db.delete_table('hr_body')

        # Deleting model 'Organization'
        db.delete_table('hr_organization')

        # Deleting model 'Worker'
        db.delete_table('hr_worker')

        # Removing M2M table for field traits on 'Worker'
        db.delete_table('hr_worker_traits')


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
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
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
        'hr.worker': {
            'Meta': {'object_name': 'Worker', '_ormbases': ['hr.Body']},
            'body_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['hr.Body']", 'unique': 'True', 'primary_key': 'True'}),
            'traits': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['hr.Trait']", 'symmetrical': 'False'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['auth.User']", 'unique': 'True'})
        }
    }

    complete_apps = ['hr']