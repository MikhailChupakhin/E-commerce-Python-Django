# Generated by Django 4.2.1 on 2023-10-05 13:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0012_subscription'),
    ]

    operations = [
        migrations.CreateModel(
            name='PromoCode',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.TextField(max_length=20, unique=True)),
                ('discount', models.DecimalField(decimal_places=2, max_digits=5)),
                ('start_date', models.DateField()),
                ('end_date', models.DateField()),
                ('max_uses', models.PositiveIntegerField()),
                ('current_uses', models.PositiveIntegerField(default=0)),
            ],
        ),
    ]
