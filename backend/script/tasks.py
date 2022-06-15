import os.path
import httplib2
import apiclient.discovery
from oauth2client.service_account import ServiceAccountCredentials
from celery import shared_task
from celery.schedules import crontab
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from datetime import datetime
from django.conf import settings
from django.core.cache import cache
import requests
from bs4 import BeautifulSoup
from .models import Order
from django.conf import settings
import requests


#Оставлю тут чтобы вы могли нормально запустить проект
CREDENTIALS_FILE = 'test-task-353212-fb8bb0700b60.json'

def telegram_bot_sendtext(bot_message):
   '''Отправляет указанное сообщение пользователю с id=TG_CHAT_ID, 
      с помощью бота с токеном = BOT_TOKEN'''
   bot_token = settings.BOT_TOKEN
   bot_chatID = settings.TG_CHAT_ID
   send_text = 'https://api.telegram.org/bot' + bot_token + '/sendMessage?chat_id=' + bot_chatID + '&parse_mode=Markdown&text=' + bot_message
   response = requests.get(send_text)
   return response.json()


def send_tg_info(id):
    '''Формирует сообщение, указывая id просроченного заказа, отправляет сообщение'''
    message = f'Товар с id={id} просрочен!'
    status = telegram_bot_sendtext(message)['ok']
    if not status:
        telegram_bot_sendtext(message)


def recalculate_db():
    '''Пересчитывает все обьекты с enabled=True по текущему курсу доллара'''
    orders = Order.objects.filter(enabled=True)
    for el in orders:
        el.price_in_rub = el.price * get_usd()
    Order.objects.bulk_update(orders, ['price_in_rub'])

@shared_task(bind=True)
def get_usd_price(self):
    '''Парсит курс доллара с сайта cbr.ru , записывает его в кеш, пересчитывает обьекты по новому курсу'''
    r = requests.get(f'https://www.cbr.ru/scripts/XML_daily.asp')
    soup = BeautifulSoup(r.text,'xml')
    dollar_tag = soup.find(attrs={"ID" : "R01235"})
    # Получаем значение курса доллара
    dollar_price = dollar_tag.select('Value')[0].get_text().replace(',', '.')
    # Записываем его в кеш
    cache.set(f"usd_price", float(dollar_price), None)
    # Пересчитываем все обьекты
    recalculate_db()


@shared_task(bind=True)
def parse(self):
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

def get_usd():
    '''Возвращает курс доллара из кеша, если там пусто, возвращает 0 и вызывает задачу которая парсит курс'''
    usd_price = cache.get("usd_price")
    if not usd_price:
        get_usd_price.delay()
        return 0
    return usd_price

def to_normal_date(str_date):
    '''Принимает строку, возвращает обьект datetime из этой строки в нужном формате'''
    return datetime.strptime(str_date, "%d.%m.%Y").date()

def if_updated(db_elem, parse_elem):
    '''Принимает обьект из базы данных, и обьект из google sheets, меняет обьект в бд,
       чтобы он соответствовал обьекту из google sheets'''
    db_elem.number = parse_elem[1]
    db_elem.price = parse_elem[2]
    db_elem.date = to_normal_date(parse_elem[3])
    db_elem.enabled = True
    db_elem.price_in_rub = int(parse_elem[2]) * get_usd()
    db_elem.save()
    # Если дата заказа раньше текущей даты, отправляем уведомление
    if to_normal_date(parse_elem[3]) < timezone.localtime(timezone.now()).date():
        send_tg_info(parse_elem[0])

def if_created(parse_elem):
    '''Принимает обьект из google sheets, создает в бд аналогичный обьект'''
    Order.objects.create(number=parse_elem[1], price=parse_elem[2],
                         date=to_normal_date(parse_elem[3]), price_in_rub=int(parse_elem[2]) * get_usd())

    # Если дата заказа раньше текущей даты, отправляем уведомление
    if to_normal_date(parse_elem[3]) < timezone.localtime(timezone.now()).date():
        send_tg_info(parse_elem[0])

def if_deleted(db_data, parse_data):
    '''Принимает список текущих обьектов в бд, и в google sheets, обьектам которые есть в бд,
       но которых нет в google sheets, cтавит enabled=False'''

    # В связи с особенностями конструкции pk в django, при удалении обьекта из бд,
    # его id не освобождается, а остается в бд. Например, если мы удалим элемент с 
    # id = 50, а затем создадим новый, он получит id=51. Из-за этой особенности могло бы
    # возникнуть много проблем в данном случае. Поэтому я принял решение не удалять обьект,
    # а как-бы скрывать его, добавляя ему enabled=False. В таком случае, если в
    # google sheets этот id вновь появится, мы изменим поля обьекта в бд на нужные,
    # и поставим ему enabled=True
    
    # Вычисляем id последнего элемента в google sheets
    last_id = int(parse_data[-1][0])
    # Вычисляем кол-во обьектов присутствующих в бд, но отсутсвующих в google sheets
    diff = db_data.count() - len(parse_data)
    # Генерируем список их id
    ids = range(last_id+1, last_id+1 + diff)
    # Получаем эти обьекты
    objs = db_data.filter(id__in=ids)
    # Ставим им enabled=False
    for el in objs:
        el.enabled = False
    Order.objects.bulk_update(objs, ['enabled'])


def make_changes(result):
    '''Проверяет каждый обьект в google sheets на соответствие с бд, 
       при несоответсвиях вызывет нужные функции'''
    db_data = Order.objects.all()
    # Идем циклом по массиву обьектов google sheets
    for el in result:
        # Пытаемся получить обьект из бд по id
        try:
            get_elem = db_data.get(id=el[0])
            # Проверяем все ли поля аналогичны
            if str(get_elem.number) != el[1] \
               or str(get_elem.price) != el[2] \
               or get_elem.date != to_normal_date(el[3]) \
               or get_elem.enabled == False:
                    if_updated(get_elem, el)  
        # Если такого обьекта нет, создаем его
        except ObjectDoesNotExist:
            if_created(el)
        # Если у обьекта что-то не так с полями или какое-то поле отсутсвует, скипаем его
        except IndexError:
            pass
    # После цикла смотрим нет ли у нас лишних обьектов в бд
    if db_data.filter(enabled=True).count() > len(result):
        if_deleted(db_data, result)


