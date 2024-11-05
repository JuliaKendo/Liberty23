# Generated by Django 4.1.7 on 2024-10-09 09:36

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0003_alter_orderitem_unit'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='deliveryaddresses',
            name='main',
        ),
        migrations.AddField(
            model_name='deliveryaddresses',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, db_index=True, default=django.utils.timezone.now, verbose_name='Дата создания'),
            preserve_default=False,
        ),
    ]