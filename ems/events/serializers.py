from rest_framework import serializers
from django.contrib.auth.models import User
from .models import UserProfile, Event, RSVP, Review

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id','username','email','first_name','last_name']

class UserProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    class Meta:
        model = UserProfile
        fields = ['user','full_name','bio','location','profile_picture']

class EventSerializer(serializers.ModelSerializer):
    organizer = UserSerializer(read_only=True)
    invited_users = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), many=True, required=False)

    class Meta:
        model = Event
        fields = ['id','title','description','organizer','location','start_time','end_time','is_public','invited_users','created_at','updated_at']
        read_only_fields = ['organizer','created_at','updated_at']

    def validate(self, attrs):
        # check start/end times
        start = attrs.get('start_time', getattr(self.instance, 'start_time', None))
        end = attrs.get('end_time', getattr(self.instance, 'end_time', None))
        if start and end and start >= end:
            raise serializers.ValidationError("start_time must be before end_time")
        return attrs

class RSVPSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    class Meta:
        model = RSVP
        fields = ['id','event','user','status','created_at','updated_at']
        read_only_fields = ['user','created_at','updated_at']

class ReviewSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    class Meta:
        model = Review
        fields = ['id','event','user','rating','comment','created_at']
        read_only_fields = ['user','created_at']

    def validate_rating(self, value):
        if not (1 <= value <= 5):
            raise serializers.ValidationError("Rating must be between 1 and 5")
        return value