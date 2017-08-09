# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-08-07 02:31
from __future__ import unicode_literals

import base.models
from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ExpenseType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('enabled', models.BooleanField(default=True)),
                ('desc', models.TextField(blank=True, null=True)),
                ('name', models.CharField(max_length=50, verbose_name='支出类型')),
            ],
            options={
                'abstract': False,
            },
            bases=(base.models.FakerMixin, models.Model),
        ),
    ]