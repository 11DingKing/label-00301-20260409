"""
Celery configuration for exam_backend project.
用于异步任务处理（阅卷、统计等）
"""
import os

from celery import Celery

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.dev')

app = Celery('exam_backend')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()

# Celery Beat Schedule (定时任务)
app.conf.beat_schedule = {
    # 每天凌晨清理过期的考试数据
    'cleanup-expired-exams': {
        'task': 'apps.exams.tasks.cleanup_expired_exams',
        'schedule': 86400.0,  # 24 hours
    },
    # 每小时更新统计数据
    'update-statistics': {
        'task': 'apps.statistics.tasks.update_statistics',
        'schedule': 3600.0,  # 1 hour
    },
}


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
