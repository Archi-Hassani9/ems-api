from django.urls import reverse
from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from rest_framework import status
from .models import Event

class EventAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='alice', password='pass')
        resp = self.client.post(reverse('token_obtain_pair'), {'username':'alice','password':'pass'}, format='json')
        self.token = resp.data['access']
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)

    def test_create_event(self):
        data = {
            'title': 'Test Event',
            'description': 'desc',
            'location': 'Online',
            'start_time': '2030-01-01T10:00:00Z',
            'end_time': '2030-01-01T12:00:00Z',
            'is_public': True
        }
        resp = self.client.post('/api/events/', data, format='json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Event.objects.count(), 1)
        self.assertEqual(Event.objects.first().organizer, self.user)
