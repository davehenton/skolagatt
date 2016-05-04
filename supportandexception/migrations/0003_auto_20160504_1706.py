# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-05-04 17:06
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0024_merge'),
        ('supportandexception', '0002_auto_20160427_1233'),
    ]

    operations = [
        migrations.CreateModel(
            name='StudentExceptionSupport',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('notes', models.CharField(max_length=500)),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='common.Student')),
            ],
        ),
        migrations.AlterField(
            model_name='exceptions',
            name='student',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='supportandexception.StudentExceptionSupport'),
        ),
        migrations.AlterField(
            model_name='supportresource',
            name='student',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='supportandexception.StudentExceptionSupport'),
        ),
    ]
