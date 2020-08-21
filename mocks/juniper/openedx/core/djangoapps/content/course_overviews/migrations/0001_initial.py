# -*- coding: utf-8 -*-
# Generated by Django 1.11.15 on 2019-07-26 02:20
from __future__ import unicode_literals

from __future__ import absolute_import
from django.db import migrations, models
import openedx.core.djangoapps.xmodule_django.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='CourseOverview',
            fields=[
                ('version', models.IntegerField()),
                ('id', openedx.core.djangoapps.xmodule_django.models.CourseKeyField(db_index=True, max_length=255, primary_key=True, serialize=False)),
                ('display_name', models.TextField(null=True)),
                ('org', models.TextField(default=b'outdated_entry', max_length=255)),
                ('display_org_with_default', models.TextField()),
                ('number', models.TextField()),
                ('created', models.DateTimeField(null=True)),
                ('start', models.DateTimeField(null=True)),
                ('end', models.DateTimeField(null=True)),
                ('enrollment_start', models.DateTimeField(null=True)),
                ('enrollment_end', models.DateTimeField(null=True)),
                ('self_paced', models.BooleanField(default=False)),
            ],
        ),
    ]