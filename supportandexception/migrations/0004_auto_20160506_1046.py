# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-05-06 10:46
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('supportandexception', '0003_auto_20160504_1706'),
    ]

    operations = [
        migrations.AlterField(
            model_name='exceptions',
            name='student',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='common.Student'),
        ),
        migrations.AlterField(
            model_name='supportresource',
            name='student',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='common.Student'),
        ),
    ]