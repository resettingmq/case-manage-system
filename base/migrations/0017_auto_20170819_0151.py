# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-08-18 17:51
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0016_auto_20170819_0058'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='trademarknationnice',
            options={'verbose_name': '分类商品/服务指定', 'verbose_name_plural': '分类商品/服务指定'},
        ),
        migrations.AlterField(
            model_name='trademarknationnice',
            name='goods',
            field=models.TextField(verbose_name='商品/服务'),
        ),
    ]