from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings

@shared_task
def send_event_notification(event_id, subject, message):
    from .models import Event
    try:
        event = Event.objects.get(pk=event_id)
    except Event.DoesNotExist:
        return False
    recipients = [u.email for u in event.invited_users.all() if u.email] + ([event.organizer.email] if event.organizer.email else [])
    recipients = list(set(recipients))
    if not recipients:
        return False
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, recipients, fail_silently=False)
    return True
