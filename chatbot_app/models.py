from django.db import models
from django.contrib.auth.models import User 
from django.utils import timezone 

class Conversation(models.Model):
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL, related_name='conversations')  # Make it nullable for now
    user_input = models.TextField()
    response = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)  # Automatically set on creation
    updated_at = models.DateTimeField(auto_now=True)  # Automatically set on update

    def __str__(self):
        return f"Conversation {self.id} by {self.user.username if self.user else 'Unknown'} on {self.created_at.strftime('%Y-%m-%d %H:%M:%S')}"

class Emotion(models.Model):
    emotion = models.TextField()