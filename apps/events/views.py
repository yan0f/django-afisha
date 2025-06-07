from datetime import timedelta

from django.db import models
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from apps.bookings.models import Booking
from apps.events.filters import EventFilter
from apps.events.models import Event
from apps.events.serializers import EventSerializer
from apps.notifications.service import EventNotificationService


class EventViewSet(viewsets.ModelViewSet):
    serializer_class = EventSerializer
    permission_classes = [IsAuthenticated]
    filterset_class = EventFilter

    def get_queryset(self):
        return Event.objects.all().order_by(
            models.Case(
                models.When(status=Event.Statuses.UPCOMING, then=0),
                models.When(status=Event.Statuses.FINISHED, then=1),
                models.When(status=Event.Statuses.CANCELLED, then=2),
                output_field=models.IntegerField(),
            ),
            'start_time',
        ).prefetch_related('tags')

    def perform_create(self, serializer):
        serializer.save(organizer=self.request.user)

    def destroy(self, request: Request, *args, **kwargs) -> Response:
        instance = self.get_object()
        if timezone.now() - instance.created_at > timedelta(hours=1):
            return Response(
                {'error': 'Удаление доступно только в течение часа после создания.'}, status=status.HTTP_400_BAD_REQUEST
            )
        return super().destroy(request, *args, **kwargs)

    @action(detail=False, methods=['get'])
    def my_events(self, request: Request) -> Response:
        events = Event.objects.filter(booking__user=request.user, start_time__gte=timezone.now())
        serializer = self.get_serializer(events, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def book(self, request: Request, pk=None) -> Response:
        event = self.get_object()

        if Booking.objects.filter(user=request.user, event=event).exists():
            return Response({'detail': 'Вы уже забронировали это событие.'}, status=status.HTTP_400_BAD_REQUEST)

        if event.seats_number <= Booking.objects.filter(event=event).count():
            return Response({'error': 'Нет свободных мест.'}, status=status.HTTP_400_BAD_REQUEST)

        Booking.objects.create(user=request.user, event=event)

        notification_service = EventNotificationService(request, event)
        notification_service.send_success_booking_notification()
        notification_service.create_booking_reminder_notification()

        return Response({'status': 'Бронь создана.'})

    @action(detail=True, methods=['post'])
    def cancel_booking(self, request: Request, pk=None) -> Response:
        event = self.get_object()

        booking = get_object_or_404(Booking, user=request.user, event=event)
        booking.delete()

        notification_service = EventNotificationService(request, event)
        notification_service.send_cancel_booking_notification()
        notification_service.delete_booking_reminder_notification()

        return Response({'status': 'Бронь отменена.'})
