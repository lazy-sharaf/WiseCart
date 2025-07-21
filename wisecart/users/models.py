from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    # Additional fields for full name and gender
    full_name = models.CharField(max_length=255)
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('N', 'Not Prefer to Say')
    ]
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, default='N')

    # User type: Basic or Premium
    USER_TYPE_CHOICES = [
        ('basic', 'Basic User'),
        ('premium', 'Premium User')
    ]
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default='basic')

    def __str__(self):
        return self.username
