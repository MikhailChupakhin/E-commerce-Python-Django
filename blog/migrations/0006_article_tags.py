# Generated by Django 4.2.1 on 2023-09-01 09:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0005_blogtag'),
    ]

    operations = [
        migrations.AddField(
            model_name='article',
            name='tags',
            field=models.ManyToManyField(to='blog.blogtag'),
        ),
    ]