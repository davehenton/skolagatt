# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-10-05 09:15
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('common', '0034_auto_20160926_0916'),
    ]

    operations = [
        migrations.CreateModel(
            name='SamraemdResult',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ra_se', models.IntegerField(max_length=3)),
                ('rm_se', models.IntegerField(max_length=3)),
                ('tt_se', models.IntegerField(max_length=3)),
                ('se', models.IntegerField(max_length=3)),
                ('ra_re', models.IntegerField(max_length=3)),
                ('rm_re', models.IntegerField(max_length=3)),
                ('tt_re', models.IntegerField(max_length=3)),
                ('re', models.IntegerField(max_length=3)),
                ('ra_sg', models.IntegerField(max_length=3)),
                ('rm_sg', models.IntegerField(max_length=3)),
                ('tt_sg', models.IntegerField(max_length=3)),
                ('sg', models.IntegerField(max_length=3)),
                ('ord_talna_txt', models.CharField(max_length=128)),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='common.Student')),
            ],
        ),
    ]