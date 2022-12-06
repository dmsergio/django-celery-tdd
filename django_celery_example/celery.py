import logging
import os

from celery import Celery
from celery.signals import after_setup_logger

from django.conf import settings


# code copied from manage.py
# set the default Django settings module for the 'celery' app.
os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "django_celery_example.settings",
)

app = Celery("Django Celery")

# read config from Django settings, the CELERY namescape would make celery
# config keys has 'CELERY' prefix
app.config_from_object("django.conf:settings", namespace="CELERY")

# discover and load tasks.py form all registred Django apps
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

@app.task
def divide(x:int, y:int):
    # from celery.contrib import rdb
    # rdb.set_trace()

    import time
    time.sleep(10)
    return x / y


@after_setup_logger.connect()
def on_after_setup_logger(logger, **kwargs):
    formatter = logger.handlers[0].formatter
    file_handler = logging.FileHandler("celery.log")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
