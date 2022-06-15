from django.db import models

# Create your models here.
class Order(models.Model):
    number = models.IntegerField(verbose_name='Номер заказа')
    price = models.IntegerField(verbose_name='Стоимость заказа в долларах')
    date = models.DateField(blank=True, null=True, verbose_name='Срок поставки')
    price_in_rub = models.DecimalField(null=True, max_digits=10, decimal_places=2, 
                                       verbose_name='Стоимость заказа в рублях')

    enabled = models.BooleanField(default=True)