# Generated by Django 4.2.1 on 2023-09-11 18:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0013_remove_article_preview'),
    ]

    operations = [
        migrations.AddField(
            model_name='blogcategory',
            name='slug',
            field=models.SlugField(blank=True, max_length=100, unique=True),
        ),
    ]
