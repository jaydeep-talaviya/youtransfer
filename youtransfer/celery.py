from celery import Celery
from django.conf import settings
import os
import django

# Create default Celery app
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'youtransfer.settings')

app = Celery('youtransfer',broker=settings.CELERY_BROKER_URL, backend=settings.CELERY_RESULT_BACKEND)

# namespace='CELERY' means all celery-related configuration keys
# should be uppercased and have a `CELERY_` prefix in Django settings.
# https://docs.celeryproject.org/en/stable/userguide/configuration.html
app.config_from_object("django.conf:settings")

# When we use the following in Django, it loads all the <appname>.tasks
# files and registers any tasks it finds in them. We can import the
# tasks files some other way if we prefer.
app.autodiscover_tasks(settings.INSTALLED_APPS)
