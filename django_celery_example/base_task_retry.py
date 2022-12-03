import celery


class BaseTaskRetry(celery.Task):
    autoretry_for = (Exception, KeyError)
    retry_kwargs = {"max_retries": 5}
    retry_backoff = True
