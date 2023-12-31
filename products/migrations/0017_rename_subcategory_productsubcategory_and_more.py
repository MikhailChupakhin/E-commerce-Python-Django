# Generated by Django 4.2.1 on 2023-07-31 15:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0016_product_preview'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='SubCategory',
            new_name='ProductSubCategory',
        ),
        migrations.AlterField(
            model_name='product',
            name='image',
            field=models.ImageField(blank=True, default='site_assets/product_image_plug.webp', upload_to='products_images/'),
        ),
        migrations.AlterField(
            model_name='product',
            name='preview',
            field=models.ImageField(blank=True, default='site_assets/product_image_plug.webp', upload_to='products_previews/'),
        ),
    ]
