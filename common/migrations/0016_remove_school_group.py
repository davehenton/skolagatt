# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-04-15 11:28
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0015_auto_20160415_1125'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='school',
            name='group',
        ),
    ]
