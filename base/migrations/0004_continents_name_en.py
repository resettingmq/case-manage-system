# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-07-04 02:24
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0003_auto_20170704_1020'),
    ]

    operations = [
        migrations.AddField(
            model_name='continents',
            name='name_en',
            field=models.CharField(db_index=True, default=None, max_length=20),
            preserve_default=False,
        ),
    ]