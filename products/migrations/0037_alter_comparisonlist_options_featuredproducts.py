# Generated by Django 4.2.1 on 2023-08-18 12:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0036_alter_product_discount_price'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='comparisonlist',
            options={'verbose_name': 'Список сравнения', 'verbose_name_plural': 'Списки сравнения'},
        ),
        migrations.CreateModel(
            name='FeaturedProducts',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('products', models.ManyToManyField(related_name='featured_products', to='products.product')),
            ],
            options={
                'verbose_name': 'Особый товар',
                'verbose_name_plural': 'Особые товары',
            },
        ),
    ]