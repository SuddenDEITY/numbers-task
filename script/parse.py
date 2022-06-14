import os.path
from re import U
import httplib2 
import apiclient.discovery
from oauth2client.service_account import ServiceAccountCredentials
from .models import Order
import datetime
from django.core.exceptions import ObjectDoesNotExist
from django.core.cache import cache
from .tasks import get_usd_price


CREDENTIALS_FILE = 'test-task-353212-fb8bb0700b60.json'

def get_usd():
    usd_price = cache.get("usd_price")
    if not usd_price:
        get_usd_price.delay()
    return usd_price

def parse():
    # Читаем ключи из файла
    credentials = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE, ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive'])
    # Авторизуемся в системе
    httpAuth = credentials.authorize(httplib2.Http()) 
    # Выбираем работу с таблицами и 4 версию API
    service = apiclient.discovery.build('sheets', 'v4', http = httpAuth) 

    spreadsheet_id = '1B2uR_2BNK0SHB3878rUThFQCRjU5umpc7AvOfMOrPBQ'
    # Получаем информацию о нашем листе
    result = service.spreadsheets().values().batchGet(spreadsheetId=spreadsheet_id,
                                                    ranges = ["A2:F"],
                                                    valueRenderOption = 'FORMATTED_VALUE').execute()
    # Берем непосредственно значения ячеек
    result = result['valueRanges'][0]['values']
    make_changes(result)

def to_normal_date(str_date):
    return datetime.datetime.strptime(str_date, "%d.%m.%Y").date()

def if_updated(db_elem, parse_elem):
    db_elem.number = parse_elem[1]
    db_elem.price = parse_elem[2]
    db_elem.date = to_normal_date(parse_elem[3])
    db_elem.enabled = True
    db_elem.save()

def if_created(parse_elem):
    Order.objects.create(number=parse_elem[1],price=parse_elem[2],date=to_normal_date(parse_elem[3]))

def if_deleted(db_data, parse_data):
    last_id = db_data.last().id
    diff = db_data.count() - len(parse_data)
    ids = range(last_id, last_id+1 + diff)
    objs = db_data.filter(id__in=ids)
    for el in objs:
        el.enabled = False
    Order.objects.bulk_update(objs, ['enabled'])


def make_changes(result):
    db_data = Order.objects.all()
    for el in result:
        try:
            get_elem = db_data.get(id=el[0])
            if str(get_elem.number) != el[1] or str(get_elem.price) != el[2] or get_elem.date != to_normal_date(el[3]) or get_elem.enabled == False:
                if_updated(get_elem, el)  

        except ObjectDoesNotExist:
            if_created(el)

    if db_data.count() > len(result):
        if_deleted(db_data, result)




            



