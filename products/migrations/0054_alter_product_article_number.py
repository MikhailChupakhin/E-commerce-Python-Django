# Generated by Django 4.2.1 on 2023-10-01 13:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0053_alter_productcharacteristic_value'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='article_number',
            field=models.CharField(editable=False, max_length=11, null=True, unique=True),
        ),
    ]