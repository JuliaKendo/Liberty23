# Generated by Django 4.1.7 on 2025-07-06 16:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0007_deliveryaddresses_date_of_birth'),
    ]

    operations = [
        migrations.AddField(
            model_name='deliveryaddresses',
            name='patronymic',
            field=models.CharField(blank=True, max_length=100, verbose_name='Отчество'),
        ),
    ]
