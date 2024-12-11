# Generated by Django 4.1.7 on 2024-12-06 18:45

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('catalog', '0003_alter_product_unit'),
    ]

    operations = [
        migrations.CreateModel(
            name='Basket',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('unit', models.CharField(choices=[('796', 'штук'), ('163', 'грамм'), ('166', 'кг')], db_index=True, default='грамм', max_length=20, verbose_name='Единица измерения')),
                ('quantity', models.PositiveIntegerField(default=1, verbose_name='Количество')),
                ('price', models.DecimalField(decimal_places=2, default=0, max_digits=8, validators=[django.core.validators.MinValueValidator(0)], verbose_name='Цена')),
                ('sum', models.DecimalField(decimal_places=2, default=0, max_digits=8, validators=[django.core.validators.MinValueValidator(0)], verbose_name='Сумма')),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='Дата создания')),
                ('product', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='cart_products', to='catalog.product', verbose_name='Номенклатура')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='cart_clients', to=settings.AUTH_USER_MODEL, verbose_name='Клиент')),
            ],
            options={
                'verbose_name': 'Заказанный товар',
                'verbose_name_plural': 'Заказанные товары',
            },
        ),
    ]
