# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date_time', models.DateTimeField(verbose_name=b'Time when created or last modified')),
                ('name', models.CharField(max_length=70, verbose_name=b'Name of the category')),
                ('description', models.TextField(verbose_name=b'Category description', blank=True)),
                ('url', models.CharField(max_length=200, verbose_name=b'Url', db_index=True)),
                ('published', models.DateTimeField(default=None, null=True, verbose_name=b'Published or not', blank=True)),
                ('lt', models.BigIntegerField(verbose_name=b'MPTT left', db_index=True)),
                ('rt', models.BigIntegerField(verbose_name=b'MPTT right')),
                ('level', models.IntegerField(verbose_name=b'Depth level in the tree')),
                ('parent', models.ForeignKey(blank=True, to='content_management.Category', null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Post',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date_time_created', models.DateTimeField(verbose_name=b'Created Time')),
                ('date_time_last_modified', models.DateTimeField(verbose_name=b'Last Modified Time')),
                ('title', models.CharField(max_length=70, verbose_name=b'Title of the post')),
                ('metadata', models.CharField(max_length=140, verbose_name=b'Metadata for seo', blank=True)),
                ('post_name', models.CharField(max_length=100, verbose_name=b'Name', db_index=True)),
                ('content', models.TextField(verbose_name=b'Content', blank=True)),
                ('excerpt', models.CharField(max_length=500, verbose_name=b'Excerpt for hidden posts or search results', blank=True)),
                ('published', models.DateTimeField(default=None, null=True, verbose_name=b'Published or not', blank=True)),
                ('draft', models.DateTimeField(default=None, null=True, verbose_name=b'Draft or not', blank=True)),
                ('hidden', models.DateTimeField(default=None, null=True, verbose_name=b'Hidden or available to all', blank=True)),
                ('trash', models.DateTimeField(default=None, null=True, verbose_name=b'If Post is deleted by user', blank=True)),
                ('user_sequence', models.IntegerField(verbose_name=b'Sequence defined by user')),
                ('sequence', models.IntegerField(verbose_name=b'Sequence by teachoo')),
                ('likes', models.IntegerField(verbose_name=b'Likes')),
                ('url', models.CharField(max_length=400, verbose_name=b'Url', db_index=True)),
                ('author', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
                ('category', models.ForeignKey(to='content_management.Category')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
