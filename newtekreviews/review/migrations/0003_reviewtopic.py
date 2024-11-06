# Generated by Django 5.0.6 on 2024-10-19 20:45

import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('review', '0002_alter_review_options'),
    ]

    operations = [
        migrations.CreateModel(
            name='ReviewTopic',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(db_index=True, max_length=200, verbose_name='Topic Title')),
                ('slug', models.SlugField(max_length=255, unique=True, validators=[django.core.validators.MinLengthValidator(3, message='Slug must be at least 3 characters long'), django.core.validators.MaxLengthValidator(200, message='Slug must be at most 200 characters long')])),
                ('text_content', models.TextField(blank=True, verbose_name='Topic Content')),
                ('review', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='topics', to='review.review')),
            ],
            options={
                'verbose_name': 'Topic',
                'verbose_name_plural': 'Topics',
            },
        ),
    ]
