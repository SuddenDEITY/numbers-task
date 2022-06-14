from celery import shared_task
from celery.schedules import crontab
from django.utils import timezone
from datetime import datetime
from django.conf import settings
from django.core.cache import cache


@shared_task(bind=True)
def get_usd_price(self):
    #function that gets usd price
    cache.set(f"usd_price", parsed_usd_price, None)