# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-04-15 11:25
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0014_auto_20160415_1040'),
    ]

    operations = [
        migrations.DeleteModel(
            name='UserMethods',
        ),
        migrations.RemoveField(
            model_name='manager',
            name='schools',
        ),
        migrations.RemoveField(
            model_name='student',
            name='schools',
        ),
        migrations.RemoveField(
            model_name='teacher',
            name='schools',
        ),
        migrations.AddField(
            model_name='school',
            name='managers',
            field=models.ManyToManyField(to='common.Manager'),
        ),
        migrations.AddField(
            model_name='school',
            name='students',
            field=models.ManyToManyField(to='common.Student'),
        ),
        migrations.AddField(
            model_name='school',
            name='teachers',
            field=models.ManyToManyField(to='common.Teacher'),
        ),
    ]
