# Generated by Django 4.2.1 on 2023-07-21 16:20

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0009_productattribute_productvariant'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='productattribute',
            options={'verbose_name': 'Аттрибут', 'verbose_name_plural': 'Аттрибуты'},
        ),
        migrations.AlterModelOptions(
            name='productvariant',
            options={'verbose_name': 'Вариант', 'verbose_name_plural': 'Варианты'},
        ),
        migrations.RemoveField(
            model_name='productvariant',
            name='price',
        ),
    ]
