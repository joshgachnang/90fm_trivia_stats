# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Score',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('team_name', models.CharField(max_length=255, db_index=True)),
                ('year', models.IntegerField()),
                ('hour', models.IntegerField(db_index=True)),
                ('place', models.IntegerField(db_index=True)),
                ('score', models.IntegerField(db_index=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('phone_number', models.CharField(db_index=True, max_length=14, unique=True, null=True, blank=True)),
                ('contact_method', models.CharField(default=b'both', max_length=16, choices=[(b'both', b'Email and Text'), (b'email', b'Email Only'), (b'text', b'Text Only'), (b'none', b'No Alerts')])),
                ('team_name', models.CharField(max_length=64, null=True, blank=True)),
                ('error_msg', models.TextField()),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='score',
            unique_together=set([('team_name', 'hour', 'year')]),
        ),
    ]
