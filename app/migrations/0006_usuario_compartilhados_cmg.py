# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-09-08 22:17
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0005_auto_20160802_1903'),
    ]

    operations = [
        migrations.AddField(
            model_name='usuario',
            name='compartilhados_cmg',
            field=models.ManyToManyField(blank=True, related_name='compartilhados_cmg', to='app.Arquivo'),
        ),
    ]