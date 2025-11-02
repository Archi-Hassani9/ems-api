from django.contrib import admin
from .models import UserProfile, Event, RSVP, Review

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user','full_name','location')

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title','organizer','start_time','is_public')
    filter_horizontal = ('invited_users',)

@admin.register(RSVP)
class RSVPAdmin(admin.ModelAdmin):
    list_display = ('event','user','status')

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('event','user','rating','created_at')
