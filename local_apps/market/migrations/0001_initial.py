# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Allocation'
        db.create_table('market_allocation', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('chore', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['design.ChoreType'])),
            ('date', self.gf('django.db.models.fields.DateField')()),
            ('days', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('market', ['Allocation'])

        # Adding model 'Assignment'
        db.create_table('market_assignment', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('is_active', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('allocation', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['market.Allocation'])),
            ('old_performer', self.gf('django.db.models.fields.related.ForeignKey')(related_name='+', to=orm['hr.Body'])),
            ('new_performer', self.gf('django.db.models.fields.related.ForeignKey')(related_name='+', to=orm['hr.Body'])),
            ('is_trade', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('transaction', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['market.Transaction'])),
        ))
        db.send_create_signal('market', ['Assignment'])

        # Adding model 'Transaction'
        db.create_table('market_transaction', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('timestamp', self.gf('django.db.models.fields.DateField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('market', ['Transaction'])

        # Adding M2M table for field signers on 'Transaction'
        db.create_table('market_transaction_signers', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('transaction', models.ForeignKey(orm['market.transaction'], null=False)),
            ('user', models.ForeignKey(orm['auth.user'], null=False))
        ))
        db.create_unique('market_transaction_signers', ['transaction_id', 'user_id'])


    def backwards(self, orm):
        # Deleting model 'Allocation'
        db.delete_table('market_allocation')

        # Deleting model 'Assignment'
        db.delete_table('market_assignment')

        # Deleting model 'Transaction'
        db.delete_table('market_transaction')

        # Removing M2M table for field signers on 'Transaction'
        db.delete_table('market_transaction_signers')


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
        },
        'market.allocation': {
            'Meta': {'object_name': 'Allocation'},
            'chore': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['design.ChoreType']"}),
            'date': ('django.db.models.fields.DateField', [], {}),
            'days': ('django.db.models.fields.IntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'market.assignment': {
            'Meta': {'object_name': 'Assignment'},
            'allocation': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['market.Allocation']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_trade': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'new_performer': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'to': "orm['hr.Body']"}),
            'old_performer': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'to': "orm['hr.Body']"}),
            'transaction': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['market.Transaction']"})
        },
        'market.transaction': {
            'Meta': {'object_name': 'Transaction'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'signers': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.User']", 'symmetrical': 'False'}),
            'timestamp': ('django.db.models.fields.DateField', [], {'auto_now_add': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['market']