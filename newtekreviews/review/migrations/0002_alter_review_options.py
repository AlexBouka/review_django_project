# Generated by Django 5.0.6 on 2024-10-11 17:08

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('review', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='review',
            options={'ordering': ['-time_created'], 'verbose_name': 'Review', 'verbose_name_plural': 'Reviews'},
        ),
    ]
