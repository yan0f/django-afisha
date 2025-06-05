from datetime import timedelta

import pytest
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from apps.bookings.models import Booking
from apps.events.models import Event
from apps.users.models import User


@pytest.mark.django_db
class TestEventViewSet(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='vfasfasfa', email='user@test.com', password='pass')
        self.organizer = User.objects.create_user(username='vfasfasfa2', email='org@test.com', password='pass')
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        self.event = Event.objects.create(
            title='Test Event',
            description='desc',
            start_time=timezone.now() + timedelta(days=1),
            location='City',
            seats_number=2,
            status=Event.Statuses.UPCOMING,
            organizer=self.organizer,
        )

    def test_list_events(self):
        url = '/api/events/'
        resp = self.client.get(url)
        assert resp.status_code == status.HTTP_200_OK

    def test_retrieve_event(self):
        url = f'/api/events/{self.event.id}/'
        resp = self.client.get(url)
        assert resp.status_code == status.HTTP_200_OK
        assert resp.data['id'] == self.event.id

    def test_create_event(self):
        url = '/api/events/'
        data = {
            'title': 'New Event',
            'description': 'desc',
            'start_time': (timezone.now() + timedelta(days=2)).isoformat(),
            'location': 'City',
            'seats_number': 10,
            'status': Event.Statuses.UPCOMING,
            'organizer': self.organizer.id,
        }
        self.client.force_authenticate(user=self.organizer)
        resp = self.client.post(url, data, format='json')
        assert resp.status_code == status.HTTP_201_CREATED

    def test_delete_event_within_hour(self):
        url = f'/api/events/{self.event.id}/'
        self.client.force_authenticate(user=self.organizer)
        resp = self.client.delete(url)
        assert resp.status_code == status.HTTP_204_NO_CONTENT

    def test_delete_event_after_hour(self):
        self.event.created_at = timezone.now() - timedelta(hours=2)
        self.event.save()
        url = f'/api/events/{self.event.id}/'
        self.client.force_authenticate(user=self.organizer)
        resp = self.client.delete(url)
        assert resp.status_code == 400

    def test_patch_status_by_organizer(self):
        url = f'/api/events/{self.event.id}/'
        self.client.force_authenticate(user=self.organizer)
        resp = self.client.patch(url, {'status': Event.Statuses.CANCELLED}, format='json')
        assert resp.status_code == status.HTTP_200_OK
        self.event.refresh_from_db()
        assert self.event.status == Event.Statuses.CANCELLED

    def test_patch_status_by_not_organizer(self):
        url = f'/api/events/{self.event.id}/'
        resp = self.client.patch(url, {'status': Event.Statuses.CANCELLED}, format='json')
        assert resp.status_code == status.HTTP_400_BAD_REQUEST

    def test_my_events(self):
        Booking.objects.create(user=self.user, event=self.event)
        url = '/api/events/my_events/'
        resp = self.client.get(url)
        assert resp.status_code == status.HTTP_200_OK
        assert len(resp.data) >= 1

    def test_book_event(self):
        url = f'/api/events/{self.event.id}/book/'
        resp = self.client.post(url)
        assert resp.status_code == status.HTTP_200_OK
        assert Booking.objects.filter(user=self.user, event=self.event).exists()

    def test_book_event_twice(self):
        Booking.objects.create(user=self.user, event=self.event)
        url = f'/api/events/{self.event.id}/book/'
        resp = self.client.post(url)
        assert resp.status_code == status.HTTP_400_BAD_REQUEST

    def test_book_event_no_seats(self):
        self.event.seats_number = 0
        self.event.save()
        url = f'/api/events/{self.event.id}/book/'
        resp = self.client.post(url)
        assert resp.status_code == status.HTTP_400_BAD_REQUEST

    def test_cancel_booking(self):
        Booking.objects.create(user=self.user, event=self.event)
        url = f'/api/events/{self.event.id}/cancel_booking/'
        resp = self.client.post(url)
        assert resp.status_code == status.HTTP_200_OK
        assert not Booking.objects.filter(user=self.user, event=self.event).exists()
