from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=60)
    last_name = models.CharField(max_length=60)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)

    # Additional profile information
    birth_date = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=10, choices=[('MALE', 'Male'), ('FEMALE', 'Female'), ('OTHER', 'Other')], null=True, blank=True)
    occupation = models.CharField(max_length=100, null=True, blank=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username", "first_name", "last_name"]

    def __str__(self):
        return self.username

    @property
    def get_initials(self):
        if self.first_name and self.last_name:
            return (self.first_name[0] + self.last_name[0]).upper()
        elif self.first_name:
            return self.first_name[0].upper()
        elif self.username:
            return self.username[0].upper()
        return "?"
