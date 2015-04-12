# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0003_auto_20150408_0637'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='subscriber',
            name='error_msg',
        ),
    ]
