# Generated by Django 5.2.1 on 2025-05-24 14:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='machine',
            name='service_company',
            field=models.CharField(blank=True, max_length=200, verbose_name='Сервисная компания'),
        ),
    ]
