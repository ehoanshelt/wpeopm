# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Category'
        db.create_table(u'projects_category', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=30)),
        ))
        db.send_create_signal(u'projects', ['Category'])

        # Adding model 'Project'
        db.create_table(u'projects_project', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('django.db.models.fields.DateField')()),
            ('acctName', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('category', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['projects.Category'])),
            ('PM', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('startDate', self.gf('django.db.models.fields.DateField')(blank=True)),
            ('endDate', self.gf('django.db.models.fields.DateField')(blank=True)),
            ('isCompleteds', self.gf('django.db.models.fields.BooleanField')()),
            ('completedDate', self.gf('django.db.models.fields.DateField')(blank=True)),
            ('isArchived', self.gf('django.db.models.fields.BooleanField')()),
            ('isDeleted', self.gf('django.db.models.fields.BooleanField')()),
        ))
        db.send_create_signal(u'projects', ['Project'])

        # Adding model 'Task'
        db.create_table(u'projects_task', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('django.db.models.fields.DateField')()),
            ('project', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['projects.Project'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('PM', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('startDate', self.gf('django.db.models.fields.DateField')(blank=True)),
            ('endDate', self.gf('django.db.models.fields.DateField')(blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')()),
            ('isCompleted', self.gf('django.db.models.fields.BooleanField')()),
            ('completedDate', self.gf('django.db.models.fields.DateField')(blank=True)),
        ))
        db.send_create_signal(u'projects', ['Task'])

        # Adding model 'Risk'
        db.create_table(u'projects_risk', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('django.db.models.fields.DateField')()),
            ('project', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['projects.Project'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('probability', self.gf('django.db.models.fields.IntegerField')(default=5)),
            ('impact', self.gf('django.db.models.fields.IntegerField')(default=5)),
            ('doesImpactCost', self.gf('django.db.models.fields.BooleanField')()),
            ('doesImpactSchedule', self.gf('django.db.models.fields.BooleanField')()),
            ('doesImpactPerformance', self.gf('django.db.models.fields.BooleanField')()),
            ('plan', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal(u'projects', ['Risk'])

        # Adding model 'Link'
        db.create_table(u'projects_link', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('django.db.models.fields.DateField')()),
            ('project', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['projects.Project'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=200, blank=True)),
            ('code', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal(u'projects', ['Link'])

        # Adding model 'Comment'
        db.create_table(u'projects_comment', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('django.db.models.fields.DateField')()),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('project', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['projects.Project'])),
            ('task', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['projects.Task'])),
            ('risk', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['projects.Risk'])),
            ('link', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['projects.Link'])),
        ))
        db.send_create_signal(u'projects', ['Comment'])


    def backwards(self, orm):
        # Deleting model 'Category'
        db.delete_table(u'projects_category')

        # Deleting model 'Project'
        db.delete_table(u'projects_project')

        # Deleting model 'Task'
        db.delete_table(u'projects_task')

        # Deleting model 'Risk'
        db.delete_table(u'projects_risk')

        # Deleting model 'Link'
        db.delete_table(u'projects_link')

        # Deleting model 'Comment'
        db.delete_table(u'projects_comment')


    models = {
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Group']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Permission']"}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'projects.category': {
            'Meta': {'ordering': "['name']", 'object_name': 'Category'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '30'})
        },
        u'projects.comment': {
            'Meta': {'object_name': 'Comment'},
            'created': ('django.db.models.fields.DateField', [], {}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'link': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['projects.Link']"}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['projects.Project']"}),
            'risk': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['projects.Risk']"}),
            'task': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['projects.Task']"})
        },
        u'projects.link': {
            'Meta': {'object_name': 'Link'},
            'code': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'created': ('django.db.models.fields.DateField', [], {}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['projects.Project']"})
        },
        u'projects.project': {
            'Meta': {'ordering': "['acctName']", 'object_name': 'Project'},
            'PM': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"}),
            'acctName': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'category': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['projects.Category']"}),
            'completedDate': ('django.db.models.fields.DateField', [], {'blank': 'True'}),
            'created': ('django.db.models.fields.DateField', [], {}),
            'endDate': ('django.db.models.fields.DateField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'isArchived': ('django.db.models.fields.BooleanField', [], {}),
            'isCompleteds': ('django.db.models.fields.BooleanField', [], {}),
            'isDeleted': ('django.db.models.fields.BooleanField', [], {}),
            'startDate': ('django.db.models.fields.DateField', [], {'blank': 'True'})
        },
        u'projects.risk': {
            'Meta': {'object_name': 'Risk'},
            'created': ('django.db.models.fields.DateField', [], {}),
            'doesImpactCost': ('django.db.models.fields.BooleanField', [], {}),
            'doesImpactPerformance': ('django.db.models.fields.BooleanField', [], {}),
            'doesImpactSchedule': ('django.db.models.fields.BooleanField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'impact': ('django.db.models.fields.IntegerField', [], {'default': '5'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'plan': ('django.db.models.fields.TextField', [], {}),
            'probability': ('django.db.models.fields.IntegerField', [], {'default': '5'}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['projects.Project']"})
        },
        u'projects.task': {
            'Meta': {'object_name': 'Task'},
            'PM': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"}),
            'completedDate': ('django.db.models.fields.DateField', [], {'blank': 'True'}),
            'created': ('django.db.models.fields.DateField', [], {}),
            'description': ('django.db.models.fields.TextField', [], {}),
            'endDate': ('django.db.models.fields.DateField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'isCompleted': ('django.db.models.fields.BooleanField', [], {}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['projects.Project']"}),
            'startDate': ('django.db.models.fields.DateField', [], {'blank': 'True'})
        }
    }

    complete_apps = ['projects']