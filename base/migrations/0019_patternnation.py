# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-08-20 12:49
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0018_pattern'),
    ]

    operations = [
        migrations.CreateModel(
            name='PatternNation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('enabled', models.BooleanField(default=True)),
                ('desc', models.TextField(blank=True, null=True, verbose_name='备注')),
                ('app_no', models.CharField(blank=True, max_length=20, null=True, verbose_name='申请号')),
                ('app_date', models.DateField(blank=True, null=True, verbose_name='申请日')),
                ('publication_no', models.CharField(blank=True, max_length=20, null=True, verbose_name='公开号')),
                ('publication_date', models.DateField(blank=True, null=True, verbose_name='公开日')),
                ('publish_no', models.CharField(blank=True, max_length=20, null=True, verbose_name='公布号')),
                ('publish_date', models.DateField(blank=True, null=True, verbose_name='公布日')),
                ('pattern_no', models.CharField(blank=True, max_length=20, null=True, verbose_name='专利号')),
                ('granted_date', models.DateField(blank=True, null=True, verbose_name='授权日')),
                ('applicant', models.CharField(blank=True, max_length=100, null=True, verbose_name='申请人')),
                ('state', models.CharField(blank=True, max_length=100, null=True, verbose_name='专利状态')),
                ('country', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='base.Country', verbose_name='申请国家')),
                ('pattern', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='base.Pattern', verbose_name='专利')),
            ],
            options={
                'verbose_name': '专利-进入国家',
                'verbose_name_plural': '专利-进入国家',
            },
        ),
    ]
