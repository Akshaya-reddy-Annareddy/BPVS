from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings

from academics.models import Course

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
    re_enroll_used = models.BooleanField(default=False) #ONE self re-enroll allowed
    allow_reenroll = models.BooleanField(default=False)
    admin_reenroll_allowed = models.BooleanField(default=False) #Admin override.

    course = models.ForeignKey(
        Course,
        on_delete=models.SET_NULL,
        null=True,
            blank=True
    )

    year = models.IntegerField(null=True, blank=True)

    def __str__(self):
        if self.role == "student":
            return self.admission_id or self.username
        elif self.role == "lecturer":
            return self.lecturer_id or self.username
        else:
            return self.admin_id or self.username
        
class Complaint(models.Model):

    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'student'}
    )

    subject = models.CharField(max_length=200)
    message = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)

    status = models.CharField(
        max_length=20,
        choices=[
            ("Open","Open"),
            ("Resolved","Resolved")
        ],
        default="Open"
    )

    def __str__(self):
        return f"{self.student} - {self.subject}"