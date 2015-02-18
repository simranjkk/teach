# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('content_management', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='metadata',
            field=models.TextField(verbose_name=b'Metadata for seo', blank=True),
        ),
    ]
