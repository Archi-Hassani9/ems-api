from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.shortcuts import get_object_or_404
from django.db import models
from .models import Event, RSVP, Review, RSVP_STATUS_CHOICES
from .serializers import EventSerializer, RSVPSerializer, ReviewSerializer
from .permissions import IsOrganizerOrReadOnly, IsInvitedOrPublic
from rest_framework.pagination import PageNumberPagination
from django.contrib.auth.models import User

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 50

class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.select_related('organizer').prefetch_related('invited_users').all()
    serializer_class = EventSerializer
    permission_classes = [IsAuthenticated, IsOrganizerOrReadOnly]
    pagination_class = StandardResultsSetPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title','location','organizer__username']

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [IsAuthenticated()]
        return super().get_permissions()

    def get_queryset(self):
        user = self.request.user
        if self.action == 'list':
            public_qs = Event.objects.filter(is_public=True)
            private_qs = Event.objects.filter(is_public=False).filter(models.Q(invited_users=user) | models.Q(organizer=user))
            # union with ordering
            return (public_qs | private_qs).distinct().order_by('-start_time')
        return super().get_queryset()

    def perform_create(self, serializer):
        event = serializer.save(organizer=self.request.user)
        # optionally trigger async email task here

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        if not instance.is_public and request.user not in instance.invited_users.all() and instance.organizer != request.user:
            return Response({"detail":"You do not have permission to view this private event."}, status=status.HTTP_403_FORBIDDEN)
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], url_path='rsvp', permission_classes=[IsAuthenticated])
    def rsvp(self, request, pk=None):
        event = self.get_object()
        if not event.is_public and request.user not in event.invited_users.all() and event.organizer != request.user:
            return Response({"detail":"Not allowed to RSVP for this private event."}, status=status.HTTP_403_FORBIDDEN)
        status_val = request.data.get('status', 'Maybe')
        if status_val not in dict(RSVP_STATUS_CHOICES):
            return Response({'detail':'Invalid status'}, status=status.HTTP_400_BAD_REQUEST)
        obj, created = RSVP.objects.update_or_create(event=event, user=request.user, defaults={'status':status_val})
        return Response(RSVPSerializer(obj).data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)

    @action(detail=True, methods=['post','get'], url_path='reviews', permission_classes=[IsAuthenticated])
    def reviews(self, request, pk=None):
        event = self.get_object()
        if request.method == 'GET':
            qs = event.reviews.all()
            page = self.paginate_queryset(qs)
            serializer = ReviewSerializer(page, many=True) if page is not None else ReviewSerializer(qs, many=True)
            return self.get_paginated_response(serializer.data) if page is not None else Response(serializer.data)
        # POST
        if not event.is_public and request.user not in event.invited_users.all() and event.organizer != request.user:
            return Response({"detail":"Not allowed to review this private event."}, status=status.HTTP_403_FORBIDDEN)
        serializer = ReviewSerializer(data={**request.data, 'event': event.id})
        if serializer.is_valid():
            serializer.save(user=request.user, event=event)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class RSVPViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def partial_update(self, request, event_pk=None, pk=None):
        event = get_object_or_404(Event, pk=event_pk)
        target_user = get_object_or_404(User, pk=pk)
        if request.user != target_user and request.user != event.organizer:
            return Response({'detail': 'Not permitted'}, status=status.HTTP_403_FORBIDDEN)
        rsvp = get_object_or_404(RSVP, event=event, user=target_user)
        status_val = request.data.get('status')
        if status_val not in dict(RSVP_STATUS_CHOICES):
            return Response({'detail':'Invalid status'}, status=status.HTTP_400_BAD_REQUEST)
        rsvp.status = status_val
        rsvp.save()
        return Response(RSVPSerializer(rsvp).data)
