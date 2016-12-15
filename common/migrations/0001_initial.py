# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-12-14 09:14
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('survey', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='GroupSurvey',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='Manager',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ssn', models.CharField(max_length=10, unique=True)),
                ('name', models.CharField(max_length=128)),
                ('email', models.CharField(blank=True, max_length=256)),
                ('phone', models.CharField(blank=True, max_length=7)),
                ('position', models.CharField(blank=True, max_length=256)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('notification_type', models.CharField(max_length=128)),
                ('notification_id', models.IntegerField()),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='School',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=128)),
                ('ssn', models.CharField(max_length=10)),
                ('managers', models.ManyToManyField(blank=True, to='common.Manager')),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Student',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ssn', models.CharField(max_length=32, unique=True)),
                ('name', models.CharField(max_length=128)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='StudentGroup',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=128)),
                ('student_year', models.CharField(blank=True, choices=[('0', 'Blandaður árgangur'), ('1', '1. bekkur'), ('2', '2. bekkur'), ('3', '3. bekkur'), ('4', '4. bekkur'), ('5', '5. bekkur'), ('6', '6. bekkur'), ('7', '7. bekkur'), ('8', '8. bekkur'), ('9', '9. bekkur'), ('10', '10. bekkur')], max_length=2, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='SurveyLogin',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('survey_id', models.CharField(max_length=256)),
                ('survey_code', models.CharField(max_length=16)),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='common.Student')),
            ],
        ),
        migrations.CreateModel(
            name='SurveyResult',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('results', models.TextField()),
                ('created_at', models.DateField(default=django.utils.timezone.now)),
            ],
        ),
        migrations.CreateModel(
            name='Teacher',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ssn', models.CharField(max_length=10, unique=True)),
                ('name', models.CharField(max_length=128)),
                ('position', models.CharField(blank=True, max_length=256)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.AddField(
            model_name='surveyresult',
            name='reported_by',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='common.Teacher'),
        ),
        migrations.AddField(
            model_name='surveyresult',
            name='student',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='common.Student'),
        ),
        migrations.AddField(
            model_name='surveyresult',
            name='survey',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='common.GroupSurvey'),
        ),
        migrations.AddField(
            model_name='studentgroup',
            name='group_managers',
            field=models.ManyToManyField(blank=True, to='common.Teacher'),
        ),
        migrations.AddField(
            model_name='studentgroup',
            name='school',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='common.School'),
        ),
        migrations.AddField(
            model_name='studentgroup',
            name='students',
            field=models.ManyToManyField(blank=True, to='common.Student'),
        ),
        migrations.AddField(
            model_name='school',
            name='students',
            field=models.ManyToManyField(blank=True, to='common.Student'),
        ),
        migrations.AddField(
            model_name='school',
            name='teachers',
            field=models.ManyToManyField(blank=True, to='common.Teacher'),
        ),
        migrations.AddField(
            model_name='groupsurvey',
            name='studentgroup',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='common.StudentGroup'),
        ),
        migrations.AddField(
            model_name='groupsurvey',
            name='survey',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='survey.Survey'),
        ),
        migrations.AlterUniqueTogether(
            name='notification',
            unique_together=set([('notification_type', 'notification_id')]),
        ),
    ]
