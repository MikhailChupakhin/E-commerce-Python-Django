# Generated by Django 4.2.1 on 2023-09-01 15:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0011_article_preview'),
    ]

    operations = [
        migrations.AlterField(
            model_name='article',
            name='image',
            field=models.ImageField(blank=True, upload_to='blog/images/'),
        ),
    ]
