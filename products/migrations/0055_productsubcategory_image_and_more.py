# Generated by Django 4.2.1 on 2024-01-23 14:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0054_alter_product_article_number'),
    ]

    operations = [
        migrations.AddField(
            model_name='productsubcategory',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='subcategory_images/'),
        ),
        migrations.AddField(
            model_name='productsubcategory',
            name='is_index_banner',
            field=models.BooleanField(default=False),
        ),
    ]
