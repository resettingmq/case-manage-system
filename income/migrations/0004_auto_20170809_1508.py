# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-08-09 07:08
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('income', '0003_income'),
    ]

    operations = [
        migrations.AlterField(
            model_name='income',
            name='currency',
            field=models.ForeignKey(default='CNY', null=True, on_delete=django.db.models.deletion.SET_NULL, to='base.Currency', verbose_name='货币'),
        ),
    ]
