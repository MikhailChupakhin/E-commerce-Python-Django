# Generated by Django 4.2.1 on 2023-07-29 15:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0014_productcharacteristic_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='image',
            field=models.ImageField(default='site_assets/product_image_plug.webp', upload_to='products_images/'),
        ),
    ]
