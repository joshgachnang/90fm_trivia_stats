# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0004_remove_subscriber_error_msg'),
    ]

    operations = [
        migrations.AlterField(
            model_name='score',
            name='year',
            field=models.IntegerField(db_index=True),
            preserve_default=True,
        ),
    ]
