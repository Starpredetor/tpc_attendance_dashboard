from celery import shared_task
from attendance.services import mark_absent_for_date


@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=True, max_retries=5)
def mark_absent_for_date_task(self, target_date=None):
    """
    Celery task to mark students ABSENT for lectures
    that occurred on target_date but were not marked PRESENT.
    """
    mark_absent_for_date(target_date)