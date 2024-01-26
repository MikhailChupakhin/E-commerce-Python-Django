# Generated by Django 4.2.1 on 2023-08-15 21:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('seo_manager', '0011_tag_slug'),
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
