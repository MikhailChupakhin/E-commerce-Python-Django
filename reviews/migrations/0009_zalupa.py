# Generated by Django 4.2.1 on 2023-09-19 12:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reviews', '0008_blogcomment'),
    ]

    operations = [
        migrations.CreateModel(
            name='Zalupa',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('data', models.CharField(max_length=255)),
                ('md5_data', models.CharField(blank=True, max_length=32, null=True)),
            ],
        ),
    ]
