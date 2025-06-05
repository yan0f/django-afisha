import json
from datetime import timedelta

from django_celery_beat.models import ClockedSchedule, PeriodicTask
from rest_framework.request import Request

from apps.events.models import Event
from apps.events.tasks import send_notification


class EventNotificationService:
    def __init__(self, request: Request, event: Event):
        self.request = request
        self.user = request.user
        self.event = event

    def send_success_booking_notification(self) -> None:
        send_notification.apply_async(
            args=[self.request.user.id, self.event.id, 'Вы успешно забронировали участие в событии.'], queue='priority'
        )

    def create_booking_reminder_notification(self) -> None:
        schedule, _ = ClockedSchedule.objects.get_or_create(clocked_time=self.event.start_time - timedelta(hours=1))

        PeriodicTask.objects.create(
            name=f'send notification to upcoming event={self.event.id} for user={self.request.user.id}',
            task='apps.events.tasks.send_notification',
            one_off=True,
            clocked=schedule,
            args=json.dumps([self.request.user.id, self.event.id, 'Событие начнется через час.']),
            queue='priority',
        )

    def send_cancel_booking_notification(self) -> None:
        send_notification.apply_async(
            args=[self.request.user.id, self.event.id, 'Вы отменили участие в событии.'], queue='priority'
        )

    def delete_booking_reminder_notification(self) -> None:
        PeriodicTask.objects.filter(
            name=f'send notification to upcoming event={self.event.id} for user={self.request.user.id}'
        ).delete()
