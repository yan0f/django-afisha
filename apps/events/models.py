from django.conf import settings
from django.contrib.postgres.indexes import GinIndex
from django.db import models


class Event(models.Model):
    class Statuses(models.TextChoices):
        UPCOMING = 'upcoming'
        CANCELLED = 'cancelled'
        FINISHED = 'finished'

    title = models.CharField(max_length=255)
    description = models.TextField()
    start_time = models.DateTimeField()
    location = models.CharField(max_length=255)
    seats_number = models.PositiveIntegerField()
    status = models.CharField(max_length=20, choices=Statuses, default=Statuses.UPCOMING)
    organizer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='organized_events')
    created_at = models.DateTimeField(auto_now_add=True)
    tags = models.ManyToManyField('tags.Tag', related_name='events')

    class Meta:
        indexes = [
            GinIndex(fields=['description']),
        ]
