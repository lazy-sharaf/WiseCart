from django.contrib.auth.models import AbstractUser
from django.db import models
import os

def user_profile_image_path(instance, filename):
    """Generate file path for user profile images"""
    # Get file extension
    ext = filename.split('.')[-1]
    # Create filename: user_id_profile.ext
    filename = f'{instance.id}_profile.{ext}'
    # Return the path: profile_pics/user_id_profile.ext
    return os.path.join('profile_pics', filename)

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
    
    # Profile picture field
    profile_picture = models.ImageField(
        upload_to=user_profile_image_path,
        null=True,
        blank=True,
        help_text="Upload your profile picture (JPG, PNG, max 5MB)"
    )

    def __str__(self):
        return self.username
    
    def get_profile_picture_url(self):
        """Return profile picture URL or default avatar"""
        if self.profile_picture and hasattr(self.profile_picture, 'url'):
            return self.profile_picture.url
        # Return a better default avatar as data URI - clean, modern design
        return 'data:image/svg+xml;charset=UTF-8,%3csvg width="200" height="200" viewBox="0 0 200 200" fill="none" xmlns="http://www.w3.org/2000/svg"%3e%3ccircle cx="100" cy="100" r="100" fill="%23E5E7EB"/%3e%3ccircle cx="100" cy="75" r="30" fill="%236B7280"/%3e%3cellipse cx="100" cy="150" rx="45" ry="35" fill="%236B7280"/%3e%3c/svg%3e'
