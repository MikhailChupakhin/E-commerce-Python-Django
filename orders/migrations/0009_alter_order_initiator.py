# Generated by Django 4.2.1 on 2023-08-21 16:35

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('orders', '0008_remove_order_basket_history_orderitem_order_items'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='initiator',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
