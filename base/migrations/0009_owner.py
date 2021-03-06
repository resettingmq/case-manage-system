# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-08-01 03:49
from __future__ import unicode_literals

import base.models
from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0008_auto_20170704_1509'),
    ]

    operations = [
        migrations.CreateModel(
            name='Owner',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('enabled', models.BooleanField(default=True)),
                ('desc', models.TextField(blank=True, null=True)),
                ('name', models.CharField(max_length=100, verbose_name='名称')),
            ],
            options={
                'abstract': False,
            },
            bases=(base.models.FakerMixin, models.Model),
        ),
    ]
