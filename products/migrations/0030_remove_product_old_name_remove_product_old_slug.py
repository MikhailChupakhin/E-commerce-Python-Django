# Generated by Django 4.2.1 on 2023-08-08 11:48

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0029_alter_product_old_name_alter_product_old_slug'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='old_name',
        ),
        migrations.RemoveField(
            model_name='product',
            name='old_slug',
        ),
    ]