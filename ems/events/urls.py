from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EventViewSet, RSVPViewSet

router = DefaultRouter()
router.register(r'events', EventViewSet, basename='events')

urlpatterns = [
    path('', include(router.urls)),
    # PATCH /api/events/{event_id}/rsvp/{user_id}/
    path('events/<int:event_pk>/rsvp/<int:pk>/', RSVPViewSet.as_view({'patch':'partial_update'}), name='event-rsvp-update'),
]
