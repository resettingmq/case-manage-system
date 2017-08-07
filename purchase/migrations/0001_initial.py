# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-08-04 14:56
from __future__ import unicode_literals

import decimal
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('base', '0009_owner'),
        ('case', '0011_auto_20170801_1201'),
    ]

    operations = [
        migrations.CreateModel(
            name='Payable',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('enabled', models.BooleanField(default=True)),
                ('desc', models.TextField(blank=True, null=True)),
                ('no', models.CharField(max_length=100, verbose_name='待付款账单编号')),
                ('received_date', models.DateField(verbose_name='收到日期')),
                ('due_date', models.DateField(verbose_name='付款期限')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='账单总金额')),
                ('unsettled_amount', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='未付金额')),
                ('settled', models.BooleanField(default=False, verbose_name='是否付清')),
                ('currency', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='base.Currency', verbose_name='货币')),
                ('subcase', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='case.SubCase', verbose_name='关联分案')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('enabled', models.BooleanField(default=True)),
                ('desc', models.TextField(blank=True, null=True)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='付款金额')),
                ('exchange_rate', models.DecimalField(blank=True, decimal_places=2, max_digits=8, null=True, verbose_name='付款汇率')),
                ('paid_date', models.DateField(verbose_name='付款日期')),
                ('transfer_charge', models.DecimalField(blank=True, decimal_places=2, default=decimal.Decimal, max_digits=7, null=True, verbose_name='手续费')),
                ('currency', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='base.Currency', verbose_name='货币')),
                ('payable', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='purchase.Payable', verbose_name='付款账单')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
