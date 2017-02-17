# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2016-11-27 16:06
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Error',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateTimeField()),
                ('process_name', models.CharField(max_length=20)),
                ('module_name', models.CharField(max_length=255)),
                ('function_name', models.CharField(max_length=255)),
                ('severity', models.CharField(choices=[('W', 'Warning'), ('E', 'Error')], max_length=1)),
                ('message', models.TextField()),
                ('actionable_info', models.TextField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Feed',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('url', models.CharField(max_length=255)),
                ('date_launched', models.DateTimeField()),
                ('date_finished', models.DateTimeField(null=True)),
                ('update_date', models.DateTimeField()),
                ('success', models.BooleanField()),
                ('info', models.TextField(null=True)),
            ],
        ),
    ]