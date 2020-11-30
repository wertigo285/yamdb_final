from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    ROLE_CHOICES = (
        ('user', 'user'),
        ('moderator', 'moderator'),
        ('admin', 'admin'),
    )

    email = models.EmailField(_('email address'), unique=True)
    role = models.CharField(
        max_length=10, choices=ROLE_CHOICES, default=ROLE_CHOICES[0][0])
    bio = models.TextField(blank=True, null=True)

    @property
    def is_admin(self):
        return bool(self.role == 'admin' or self.is_staff)

    @property
    def is_moderator(self):
        return bool(self.role == 'moderator')
