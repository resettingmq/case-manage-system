# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-07-12 07:19
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
            name='Stage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('enabled', models.BooleanField(default=True)),
                ('name', models.CharField(max_length=100)),
            ],
            options={
                'abstract': False,
            },
            bases=(base.models.FakerMixin, models.Model),
        ),
    ]
