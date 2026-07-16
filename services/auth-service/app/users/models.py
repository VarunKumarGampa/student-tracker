from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Custom user model for the student tracking system.
    Extends AbstractUser so we keep all built-in auth
    behaviour and just add our own fields on top.
    """

    class Role(models.TextChoices):
        STUDENT = 'student', 'Student'
        TEACHER = 'teacher', 'Teacher'
        ADMIN   = 'admin',   'Admin'

    role    = models.CharField(
        max_length=10,
        choices=Role.choices,
        default=Role.STUDENT,
    )
    grade   = models.CharField(
        max_length=20,
        blank=True,    # optional — only students have a grade
        null=True,
    )
    subject = models.CharField(
        max_length=100,
        blank=True,    # optional — only teachers have a subject
        null=True,
    )

    # Use email as the login field instead of username
    email    = models.EmailField(unique=True)
    USERNAME_FIELD  = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return f'{self.email} ({self.role})'

    @property
    def is_student(self):
        return self.role == self.Role.STUDENT

    @property
    def is_teacher(self):
        return self.role == self.Role.TEACHER