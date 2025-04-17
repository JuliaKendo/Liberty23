# Generated by Django 4.1.7 on 2025-04-16 09:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('enterprise', '0009_integrationsettings'),
        ('catalog', '0004_product_weight'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='departments',
            field=models.ManyToManyField(related_name='department_products', to='enterprise.department', verbose_name='Подразделения'),
        ),
    ]
