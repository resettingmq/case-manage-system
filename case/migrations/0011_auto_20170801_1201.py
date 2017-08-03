# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-08-01 04:01
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0009_owner'),
        ('case', '0010_subcase'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='case',
            name='is_private',
        ),
        migrations.AddField(
            model_name='case',
            name='owner',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='base.Owner'),
        ),
        migrations.AlterField(
            model_name='subcase',
            name='agent',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='agent_subcase', to='base.Client', verbose_name='代理'),
        ),
        migrations.AlterField(
            model_name='subcase',
            name='case',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='case.Case', verbose_name='所属案件'),
        ),
        migrations.AlterField(
            model_name='subcase',
            name='closed',
            field=models.BooleanField(default=False, verbose_name='结案'),
        ),
        migrations.AlterField(
            model_name='subcase',
            name='name',
            field=models.CharField(max_length=200, verbose_name='分案名'),
        ),
        migrations.AlterField(
            model_name='subcase',
            name='settled',
            field=models.BooleanField(default=False, verbose_name='款项结清'),
        ),
        migrations.AlterField(
            model_name='subcase',
            name='stage',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='case.Stage', verbose_name='所处阶段'),
        ),
    ]
