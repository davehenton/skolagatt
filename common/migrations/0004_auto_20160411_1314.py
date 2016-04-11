# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-04-11 13:14
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0003_auto_20160411_1309'),
    ]

    operations = [
        migrations.AddField(
            model_name='manager',
            name='schools',
            field=models.ManyToManyField(to='common.School'),
        ),
        migrations.AddField(
            model_name='student',
            name='schools',
            field=models.ManyToManyField(to='common.School'),
        ),
        migrations.AddField(
            model_name='teacher',
            name='schools',
            field=models.ManyToManyField(to='common.School'),
        ),
    ]