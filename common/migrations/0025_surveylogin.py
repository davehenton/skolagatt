# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-06-01 14:14
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0024_merge'),
    ]

    operations = [
        migrations.CreateModel(
            name='SurveyLogin',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('survey_id', models.CharField(max_length=256)),
                ('survey_code', models.CharField(max_length=16)),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='common.Student')),
            ],
        ),
    ]
