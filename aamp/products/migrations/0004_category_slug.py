# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-03-15 09:39
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0003_auto_20160312_1057'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='slug',
            field=models.SlugField(default=1),
            preserve_default=False,
        ),
    ]
