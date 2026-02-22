from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLE_CHOICES = (
        ('student', 'Student'),
        ('lecturer', 'Lecturer'),
        ('admin', 'Admin'),
    )

    role = models.CharField(max_length=10, choices=ROLE_CHOICES)

    # Student fields
    admission_id = models.CharField(max_length=20, unique=True, null=True, blank=True)
    dob = models.DateField(null=True, blank=True)

    # Lecturer fields
    lecturer_id = models.CharField(max_length=20, unique=True, null=True, blank=True)

    # Admin fields
    admin_id = models.CharField(max_length=20, unique=True, null=True, blank=True)

    # Face enrollment status (VERY IMPORTANT)
    face_enrolled = models.BooleanField(default=False)

    def __str__(self):
        if self.role == "student":
            return self.admission_id
        elif self.role == "lecturer":
            return self.lecturer_id
        else:
            return self.admin_id