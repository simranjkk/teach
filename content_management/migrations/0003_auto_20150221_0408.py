# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('content_management', '0002_auto_20150218_1623'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='post',
            name='excerpt',
        ),
        migrations.RemoveField(
            model_name='post',
            name='metadata',
        ),
        migrations.AddField(
            model_name='post',
            name='keywords',
            field=models.CharField(default='default-title', max_length=500, verbose_name=b'space separated keywords', blank=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='post',
            name='transcript',
            field=models.TextField(default='default-transcript', verbose_name=b'Transcript: text version of image or other form', blank=True),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='post',
            name='title',
            field=models.CharField(max_length=140, verbose_name=b'Title of the post'),
        ),
    ]
