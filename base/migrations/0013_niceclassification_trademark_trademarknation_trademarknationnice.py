# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-08-16 15:44
from __future__ import unicode_literals

import base.models
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0012_client_email'),
    ]

    operations = [
        migrations.CreateModel(
            name='NiceClassification',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('enabled', models.BooleanField(default=True)),
                ('desc', models.TextField(blank=True, null=True, verbose_name='备注')),
                ('name', models.CharField(max_length=10, verbose_name='分类名称')),
            ],
            options={
                'verbose_name': '尼斯分类',
                'verbose_name_plural': '尼斯分类',
            },
            bases=(base.models.FakerMixin, models.Model),
        ),
        migrations.CreateModel(
            name='Trademark',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('enabled', models.BooleanField(default=True)),
                ('desc', models.TextField(blank=True, null=True, verbose_name='备注')),
                ('name', models.CharField(max_length=200, verbose_name='商标名称')),
                ('client', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='base.Client', verbose_name='所属客户')),
            ],
            options={
                'verbose_name': '商标',
                'verbose_name_plural': '商标',
            },
        ),
        migrations.CreateModel(
            name='TrademarkNation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('enabled', models.BooleanField(default=True)),
                ('desc', models.TextField(blank=True, null=True, verbose_name='备注')),
                ('app_no', models.CharField(blank=True, max_length=20, null=True, verbose_name='申请号')),
                ('app_date', models.DateField(blank=True, null=True, verbose_name='申请日')),
                ('applicant', models.CharField(blank=True, max_length=100, null=True, verbose_name='申请人')),
                ('state', models.CharField(blank=True, max_length=100, null=True, verbose_name='商标状态')),
                ('country', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='base.Country', verbose_name='申请国家')),
                ('trademark', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='base.Trademark', verbose_name='商标')),
            ],
            options={
                'verbose_name': '商标-国家',
                'verbose_name_plural': '商标-国家',
            },
        ),
        migrations.CreateModel(
            name='TrademarkNationNice',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('enabled', models.BooleanField(default=True)),
                ('desc', models.TextField(blank=True, null=True, verbose_name='备注')),
                ('goods', models.CharField(max_length=400, verbose_name='商品/服务')),
                ('nice_class', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='base.NiceClassification', verbose_name='尼斯分类')),
                ('trademark_nation', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='base.TrademarkNation', verbose_name='商标-国家')),
            ],
            options={
                'verbose_name': '商标分类',
                'verbose_name_plural': '商标分类',
            },
        ),
    ]