# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-08-18 13:44
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0013_niceclassification_trademark_trademarknation_trademarknationnice'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='trademarknation',
            options={'verbose_name': '商标-进入国家', 'verbose_name_plural': '商标-进入国家'},
        ),
    ]
