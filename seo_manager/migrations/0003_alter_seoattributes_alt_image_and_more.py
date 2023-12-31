# Generated by Django 4.2.1 on 2023-08-01 17:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('seo_manager', '0002_alter_seoattributes_options_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='seoattributes',
            name='alt_image',
            field=models.CharField(blank=True, max_length=200),
        ),
        migrations.AlterField(
            model_name='seoattributes',
            name='meta_description',
            field=models.CharField(blank=True, max_length=300),
        ),
        migrations.AlterField(
            model_name='seoattributes',
            name='page_url',
            field=models.TextField(unique=True),
        ),
        migrations.AlterField(
            model_name='seoattributes',
            name='title',
            field=models.CharField(blank=True, max_length=200),
        ),
    ]
