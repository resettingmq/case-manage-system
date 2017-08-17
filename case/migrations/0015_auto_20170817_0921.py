# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-08-17 01:21
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0013_niceclassification_trademark_trademarknation_trademarknationnice'),
        ('case', '0014_auto_20170811_0158'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='case',
            name='entry_country',
        ),
        migrations.AddField(
            model_name='subcase',
            name='category',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='case.Category', verbose_name='案件类型'),
        ),
        migrations.AddField(
            model_name='subcase',
            name='entry_country',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='base.Country', verbose_name='进入国家'),
        ),
        migrations.AlterField(
            model_name='case',
            name='category',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='case.Category', verbose_name='案件类型'),
        ),
    ]
