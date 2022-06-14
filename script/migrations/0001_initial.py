# Generated by Django 4.0.5 on 2022-06-13 14:30

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.IntegerField(verbose_name='Номер заказа')),
                ('price', models.IntegerField(verbose_name='Стоимость заказа $')),
                ('date', models.DateField(blank=True, null=True, verbose_name='Срок поставки')),
            ],
        ),
    ]
