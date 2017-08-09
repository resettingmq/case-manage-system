# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-08-09 02:43
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('purchase', '0003_remove_payment_transfer_charge'),
    ]

    operations = [
        migrations.AlterField(
            model_name='payment',
            name='exchange_rate',
            field=models.DecimalField(decimal_places=4, max_digits=8, verbose_name='付款汇率'),
        ),
    ]