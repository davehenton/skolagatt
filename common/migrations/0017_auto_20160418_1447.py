# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-04-18 14:47
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0016_remove_school_group'),
    ]

    operations = [
        migrations.CreateModel(
            name='SurveyResult',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('completed_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('results', models.TextField()),
                ('survey', models.CharField(max_length=1024)),
                ('reported_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='common.Teacher')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='common.Student')),
            ],
        ),
        migrations.AlterField(
            model_name='studentgroup',
            name='group_managers',
            field=models.ManyToManyField(blank=True, to='common.Teacher'),
        ),
    ]