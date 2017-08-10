# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-08-10 01:19
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('case', '0011_auto_20170801_1201'),
        ('purchase', '0004_auto_20170809_1043'),
    ]

    operations = [
        migrations.CreateModel(
            name='PaymentLink',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('enabled', models.BooleanField(default=True)),
                ('desc', models.TextField(blank=True, null=True)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='转移金额')),
                ('payment', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='purchase.Payment', verbose_name='已付账单')),
                ('subcase', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='case.SubCase', verbose_name='转移目标(分案件)')),
            ],
            options={
                'verbose_name_plural': '已付款转移',
                'verbose_name': '已付款转移',
            },
        ),
    ]