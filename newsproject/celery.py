import os
import django
from celery import Celery
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'newsproject.settings')
django.setup()

app = Celery('news')

app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

CELERYBEAT_SCHEDULER = "djcelery.schedulers.DatabaseScheduler"
# CELERYBEAT_SCHEDULE = {
#     "get_articles": {
#         'task': "news.tasks.parse",
#         'schedule': timedelta(seconds=60),
#     },
# }
