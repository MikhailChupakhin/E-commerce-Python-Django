# Generated by Django 4.2.1 on 2023-08-12 11:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0030_remove_product_old_name_remove_product_old_slug'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='is_new',
            field=models.BooleanField(default=False),
        ),
    ]
