# Generated by Django 4.2.1 on 2023-09-10 20:17

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0044_manufacturer_product_manufacturer'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='manufacturer',
            options={'verbose_name': 'Производитель', 'verbose_name_plural': 'Производители'},
        ),
    ]