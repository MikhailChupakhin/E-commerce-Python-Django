from __future__ import absolute_import, unicode_literals

import os

from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'store.settings')

app = Celery('store')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks(['store.tasks', 'orders.tasks'])

# celery -A store worker -l INFO -n worker3 -P solo
# celery -A store beat -l debug
