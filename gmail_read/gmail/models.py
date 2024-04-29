from django.db import models
from django.contrib.auth.models import User


class Emails(models.Model):
    email_from = models.EmailField(blank=True, null=True)
    email_to = models.EmailField(blank=True, null=True)
    email_subject = models.CharField(max_length=500, blank=True, null=True)
    message_id = models.CharField(max_length=100, blank=True, null=True)
    email_message = models.TextField(blank=True, null=True)
    email_received_date = models.DateTimeField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
