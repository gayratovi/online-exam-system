from django.contrib.auth.models import AbstractUser
from django.db import models

class Module(models.Model):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=32, unique=True)

    def __str__(self):
        return f"{self.code} — {self.name}"

class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('student', 'Student'),
        ('staff', 'Staff'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='student')

    # For STAFF (teacher) — exactly one module
    module = models.ForeignKey(
        Module, on_delete=models.SET_NULL, null=True, blank=True, related_name='staff_members'
    )

    # For STUDENTS — zero or many modules
    modules = models.ManyToManyField(Module, blank=True, related_name='students')

    def __str__(self):
        return f"{self.username} ({self.role})"
