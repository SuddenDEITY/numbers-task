from celery import shared_task
from celery.schedules import crontab
from django.utils import timezone
from datetime import datetime
from django.conf import settings
from django.core.cache import cache
import requests
from bs4 import BeautifulSoup


@shared_task(bind=True)
def get_usd_price(self):
    '''Parse usd and eur price from cbr.ru'''
    r = requests.get(f'https://www.cbr.ru/scripts/XML_daily.asp')
    soup = BeautifulSoup(r.text,'xml')
    dollar_tag = soup.find(attrs={"ID" : "R01235"})
    dollar_price = dollar_tag.select('Value')[0].get_text().replace(',', '.')
    cache.set(f"usd_price", float(dollar_price), None)