# Generated by Django 4.2.1 on 2023-09-02 13:14

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0041_product_article_number'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='preview',
        ),
    ]