# Generated by Django 4.2.1 on 2023-09-12 15:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('seo_manager', '0013_delete_subscription'),
    ]

    operations = [
        migrations.AlterField(
            model_name='seoattributes',
            name='alt_image',
            field=models.CharField(blank=True, default='', max_length=200),
        ),
    ]
