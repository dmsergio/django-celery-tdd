import random

import requests
from celery import shared_task
from celery.signals import task_postrun
from celery.utils.log import get_task_logger
from django.contrib.auth.models import User
from django.db import transaction

from django_celery_example.base_task_retry import BaseTaskRetry
from polls.consumers import notify_channel_layer


logger = get_task_logger(__name__)


@shared_task()
def sample_task(email):
    from polls.views import api_call

    api_call(email)


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_kwargs={
        "max_retries": 5,  # default=3; None is to disable the retry limit
        # "countdown": 5,  # 5 seconds after retry the failed task
    },
    retry_backoff=True,  # exponential retry time; if a number is set, it is used as a delay factor
    # time_limit=10,  # hard time limit, in seconds, for this task
    # soft_time_limit=10,  # soft time limit for this task
)
def task_process_notification(self):
    # try:
    if not random.choice([0, 1]):
        raise Exception()
    requests.post("https://httpbin.org/delay/5")
    # except Exception as e:
    #     logger.error("exception raised, it would be retry after 5 seconds")
    #     raise self.retry(exc=e, countdown=5)


@shared_task()
def task_send_welcome_email(user_pk):
    user = User.objects.get(pk=user_pk)
    logger.info(f"send email to {user.email} {user.pk}")


@shared_task(bind=True, base=BaseTaskRetry)
def task_process_notification_base_retry(self):
    raise Exception()


@task_postrun.connect
def task_postrun_handler(task_id, **kwargs):
    """
    When celery task finish, send notification to Django channel_layer, so
    Django channel would receive the event and then send it to web client
    """
    notify_channel_layer(task_id)


@shared_task(name="task_clear_session")
def task_clear_session():
    from django.core.management import call_command
    call_command("clearsessions")


@shared_task(name="default:dynamic_example_one")
def dynamic_example_one():
    logger.info("Example one")


@shared_task(name="low_priority:dynamic_example_two")
def dynamic_example_two():
    logger.info("Example two")


@shared_task(name="high_priority:dynamic_example_three")
def dynamic_example_three():
    logger.info("Example three")


@shared_task()
def task_transaction_test():
    with transaction.atomic():
        from .views import random_username
        username = random_username()
        user = User.objects.create_user(username, 'lennon@thebeatles.com', 'johnpassword')
        user.save()
        logger.info(f'send email to {user.pk}')
        raise Exception('test')
