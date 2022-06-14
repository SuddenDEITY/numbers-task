from django.db import models

# Create your models here.
class Order(models.Model):
    number = models.IntegerField(verbose_name='Номер заказа')
    price = models.IntegerField(verbose_name='Стоимость заказа $')
    date = models.DateField(blank=True, null=True, verbose_name='Срок поставки')
    enabled = models.BooleanField(default=True)