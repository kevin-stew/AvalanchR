from celery import Celery
from config import Config

app = Celery('tasks', broker=Config.CELERY_BROKER_URL)

@app.task
def add(x, y):
    return x + y