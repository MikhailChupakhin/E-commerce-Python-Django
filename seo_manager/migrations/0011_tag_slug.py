# Generated by Django 4.2.1 on 2023-08-14 18:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('seo_manager', '0010_alter_tag_options'),
    ]

    operations = [
        migrations.AddField(
            model_name='tag',
            name='slug',
            field=models.SlugField(blank=True, unique=True),
        ),
    ]
