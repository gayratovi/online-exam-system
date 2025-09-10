from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models


class Module(models.Model):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=32, unique=True)

    def __str__(self):
        return f"{self.code} — {self.name}"


class CustomUserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, username, email, password, **extra_fields):
        if not username:
            raise ValueError("The Username must be set")
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        extra_fields.setdefault("role", "student")  # default
        return self._create_user(username, email, password, **extra_fields)

    def create_superuser(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("role", "admin")  # force admin role
        return self._create_user(username, email, password, **extra_fields)


class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('student', 'Student'),
        ('staff', 'Staff'),
        ("admin", "Admin"),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='student')

    # For STAFF (teacher) — exactly one module
    module = models.ForeignKey(
        Module, on_delete=models.SET_NULL, null=True, blank=True, related_name='staff_members'
    )

    # For STUDENTS — zero or many modules
    modules = models.ManyToManyField(Module, blank=True, related_name='students')

    objects = CustomUserManager()   # ✅ attach manager

    def __str__(self):
        return f"{self.username} ({self.role})"
