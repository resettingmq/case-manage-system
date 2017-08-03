# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-07-12 07:45
from __future__ import unicode_literals

import base.models
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0008_auto_20170704_1509'),
        ('case', '0004_auto_20170712_1527'),
    ]

    operations = [
        migrations.CreateModel(
            name='Case',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('enabled', models.BooleanField(default=True)),
                ('name', models.CharField(max_length=200)),
                ('archive_no', models.CharField(blank=True, max_length=100, null=True)),
                ('is_private', models.BooleanField(default=False)),
                ('settled', models.BooleanField(default=False)),
                ('closed', models.BooleanField(default=False)),
                ('category', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='case.Category')),
                ('client', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='base.Client')),
                ('entry_country', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='base.Country')),
                ('stage', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='case.Stage')),
            ],
            options={
                'abstract': False,
            },
            bases=(base.models.FakerMixin, models.Model),
        ),
    ]