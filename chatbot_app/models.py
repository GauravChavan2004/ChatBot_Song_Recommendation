from django.db import models

class Conversation(models.Model):
    user_input = models.TextField()
    response = models.TextField()