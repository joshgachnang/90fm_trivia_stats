# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import website.models


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0002_auto_20150330_0033'),
    ]

    operations = [
        migrations.CreateModel(
            name='Subscriber',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('phone_number', models.CharField(max_length=14, null=True, blank=True)),
                ('email', models.EmailField(max_length=75, null=True, blank=True)),
                ('team_name', models.CharField(default=None, max_length=64, null=True, blank=True)),
                ('error_msg', models.TextField()),
                ('delete_code', models.CharField(default=website.models.random_code, max_length=8, null=True, blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.RemoveField(
            model_name='userprofile',
            name='user',
        ),
        migrations.DeleteModel(
            name='UserProfile',
        ),
    ]
