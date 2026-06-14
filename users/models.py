"""
Custom User model with extended profile fields.
"""

from django.contrib.auth.models import AbstractUser
from django.db import models
from cloudinary.models import CloudinaryField


class User(AbstractUser):
    """Extended user model with address and profile information."""

    email = models.EmailField(unique=True)
    avatar = CloudinaryField('avatar', blank=True, null=True,
                             folder='avatars/')
    phone_number = models.CharField(max_length=20, blank=True)

    # Address fields
    street_name = models.CharField(max_length=255, blank=True)
    building_number = models.CharField(max_length=50, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)
    city = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True, default='Sweden')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-created_at']

    def __str__(self):
        return self.email

    def get_full_address(self):
        """Return formatted full address."""
        parts = [
            self.street_name,
            self.building_number,
            self.postal_code,
            self.city,
            self.country,
        ]
        return ', '.join(p for p in parts if p)

    def has_complete_address(self):
        """Check if user has a complete shipping address."""
        return all([
            self.street_name,
            self.postal_code,
            self.city,
            self.country,
        ])

    @property
    def avatar_url(self):
        """Return avatar URL or default."""
        if self.avatar:
            return self.avatar.url
        return '/static/images/default-avatar.png'

    def can_delete_account(self):
        """Only non-admin/non-staff users can delete their accounts."""
        return not self.is_staff and not self.is_superuser
