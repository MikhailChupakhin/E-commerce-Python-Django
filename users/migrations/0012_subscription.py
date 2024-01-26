# Generated by Django 4.2.1 on 2023-08-15 22:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0011_callbackquery'),
    ]

    operations = [
        migrations.CreateModel(
            name='Subscription',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]