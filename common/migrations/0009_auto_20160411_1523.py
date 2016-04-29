# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-04-11 15:23
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0008_auto_20160411_1455'),
    ]

    operations = [
        migrations.AddField(
            model_name='studentgroup',
            name='group_managers',
            field=models.ManyToManyField(to='common.Teacher'),
        ),
        migrations.AlterField(
            model_name='student',
            name='student_groups',
            field=models.ManyToManyField(blank=True, to='common.StudentGroup'),
        ),
    ]