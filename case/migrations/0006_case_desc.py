# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-07-12 08:13
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('case', '0005_case'),
    ]

    operations = [
        migrations.AddField(
            model_name='case',
            name='desc',
            field=models.TextField(blank=True, null=True),
        ),
    ]
