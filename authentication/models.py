from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    # The `id` field is inherited from AbstractUser (primary key, auto-increment).
    email = models.EmailField(unique=True)  # Make email unique
    role = models.CharField(max_length=50, default="user")  # Add role field

    # Ensure email is used as the unique identifier for authentication
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']  # Remove email from required fields since it's the unique identifier

    def __str__(self):
        return self.email
