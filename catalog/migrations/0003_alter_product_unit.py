# Generated by Django 4.1.7 on 2024-09-11 13:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0002_remove_product_available_for_order_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='unit',
            field=models.CharField(choices=[('796', 'штук'), ('163', 'грамм'), ('166', 'кг')], db_index=True, default='штук', max_length=20, verbose_name='Единица измерения'),
        ),
    ]
