# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-08-20 15:56
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0019_patternnation'),
        ('case', '0019_case_pattern'),
    ]

    operations = [
        migrations.AddField(
            model_name='subcase',
            name='patternnation',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='base.PatternNation', verbose_name='专利-进入国家'),
        ),
    ]
