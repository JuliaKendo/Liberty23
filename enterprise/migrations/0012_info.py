# Generated by Django 4.1.7 on 2025-04-28 11:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('enterprise', '0011_integrationsettings_login_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Info',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(db_index=True, max_length=200, verbose_name='Заголовок')),
                ('picture', models.ImageField(blank=True, null=True, upload_to='pictures_news', verbose_name='Изображение')),
                ('content', models.TextField(blank=True, verbose_name='Содержание')),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='Дата создания')),
            ],
            options={
                'verbose_name': 'Информация',
                'verbose_name_plural': 'Информация',
            },
        ),
    ]
