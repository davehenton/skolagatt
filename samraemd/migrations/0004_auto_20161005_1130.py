# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-10-05 11:30
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('samraemd', '0003_auto_20161005_0925'),
    ]

    operations = [
        migrations.AddField(
            model_name='samraemdislresult',
            name='exam_code',
            field=models.CharField(default='', max_length=128),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='samraemdmathresult',
            name='exam_code',
            field=models.CharField(default='', max_length=128),
            preserve_default=False,
        ),
    ]
