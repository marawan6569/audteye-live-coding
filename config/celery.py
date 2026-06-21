import os

from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('audteye')

app.config_from_object('django.conf:settings', namespace='CELERY')

# task_acks_late + task_reject_on_worker_lost: the broker re-delivers a task
# if the worker crashes or is killed mid-execution. This is a deliberate
# production-style choice; do not change it.
app.conf.task_acks_late = True
app.conf.task_reject_on_worker_lost = True

app.autodiscover_tasks()
