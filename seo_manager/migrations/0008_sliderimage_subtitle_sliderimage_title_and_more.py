# Generated by Django 4.2.1 on 2023-08-10 11:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('seo_manager', '0007_redirect_created_at'),
    ]

    operations = [
        migrations.AddField(
            model_name='sliderimage',
            name='subtitle',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name='sliderimage',
            name='title',
            field=models.CharField(blank=True, max_length=120),
        ),
        migrations.AlterField(
            model_name='sliderimage',
            name='alt_text',
            field=models.CharField(blank=True, max_length=255),
        ),
    ]
