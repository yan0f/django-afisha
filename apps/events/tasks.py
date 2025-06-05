from datetime import timedelta

from celery import shared_task
from django.utils.timezone import now

from apps.events.models import Event
from apps.notifications.models import Notification


@shared_task
def update_event_statuses() -> None:
    events = Event.objects.filter(status=Event.Statuses.UPCOMING, start_time__lte=now() - timedelta(hours=2))
    for event in events:
        event.status = Event.Statuses.FINISHED
    Event.objects.bulk_update(events, ['status'])


@shared_task
def send_notification(user_id: int, event_id: int, message: str) -> None:
    Notification.objects.create(user_id=user_id, event_id=event_id, message=message)
    print(f'{user_id=}, {event_id=}, {message=}')
