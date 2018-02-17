# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2018-02-06 07:18
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('genRisks', '0002_currencyfield_numberfield'),
    ]

    operations = [
        migrations.CreateModel(
            name='dateField',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_field_name', models.DateField()),
                ('generic_risk', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='genRisks.GenericRisk')),
            ],
        ),
        migrations.RemoveField(
            model_name='currencyfield',
            name='date_field_name',
        ),
        migrations.AddField(
            model_name='currencyfield',
            name='currency_field_name',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='numberfield',
            name='number_field_name',
            field=models.IntegerField(default=0),
        ),
    ]
