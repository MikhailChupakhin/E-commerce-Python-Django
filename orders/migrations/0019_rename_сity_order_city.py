# Generated by Django 4.2.1 on 2023-09-19 12:26

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0018_order_delivery_method_order_payment_method'),
    ]

    operations = [
        migrations.RenameField(
            model_name='order',
            old_name='сity',
            new_name='city',
        ),
    ]
