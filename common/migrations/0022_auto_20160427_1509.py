# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-04-27 15:09
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0021_remove_surveyresult_completed_at'),
    ]

    operations = [
        migrations.AlterField(
            model_name='school',
            name='managers',
            field=models.ManyToManyField(blank=True, to='common.Manager'),
        ),
        migrations.AlterField(
            model_name='school',
            name='students',
            field=models.ManyToManyField(blank=True, to='common.Student'),
        ),
        migrations.AlterField(
            model_name='school',
            name='teachers',
            field=models.ManyToManyField(blank=True, to='common.Teacher'),
        ),
    ]
