# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-08-07 08:29
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sale', '0007_auto_20170807_0959'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='receipts',
            name='transfer_charge',
        ),
    ]