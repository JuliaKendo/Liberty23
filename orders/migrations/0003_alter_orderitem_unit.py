# Generated by Django 4.1.7 on 2024-10-08 15:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0002_alter_order_delivery_address'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderitem',
            name='unit',
            field=models.CharField(choices=[('796', 'штук'), ('163', 'грамм'), ('166', 'кг')], db_index=True, default='грамм', max_length=20, verbose_name='Единица измерения'),
        ),
    ]
