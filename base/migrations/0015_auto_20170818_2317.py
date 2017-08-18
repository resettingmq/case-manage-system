# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-08-18 15:17
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0014_auto_20170818_2144'),
    ]

    operations = [
        migrations.AddField(
            model_name='trademarknation',
            name='register_date',
            field=models.DateField(blank=True, null=True, verbose_name='注册日'),
        ),
        migrations.AddField(
            model_name='trademarknation',
            name='register_no',
            field=models.CharField(blank=True, max_length=20, null=True, verbose_name='注册号'),
        ),
    ]