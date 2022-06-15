from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from celery.signals import worker_ready

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
app = Celery('config')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()


@worker_ready.connect
def at_start(sender, **k):
    '''Используем сигнал worker_ready, чтобы при запуске воркера выполнять функцию get_usd_price'''
    # Так как кеш очищается при перезапуске, требуется получать курс доллара сразу после старта.
    # Чтобы не словить тайминг с пустым кешем.
    with sender.app.connection() as conn:
         sender.app.send_task('script.tasks.get_usd_price', connection=conn)