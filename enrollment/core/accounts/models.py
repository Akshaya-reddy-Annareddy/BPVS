from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.contrib.auth.hashers import make_password


class StudentManager(BaseUserManager):
    def create_user(self, admission_id, dob, password=None, **extra_fields):
        if not admission_id:
            raise ValueError("Admission ID is required")

        user = self.model(
            admission_id=admission_id,
            dob=dob,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, admission_id, dob, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'admin')

        return self.create_user(admission_id, dob, password, **extra_fields)


class Course(models.Model):
    course_name = models.CharField(max_length=100)
    course_code = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return f"{self.course_code} - {self.course_name}"


class Student(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = (
        ('student', 'Student'),
        ('teacher', 'Teacher'),
        ('admin', 'Admin'),
    )

    admission_id = models.CharField(max_length=20, unique=True)
    dob = models.DateField()
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='student')

    # Face enrollment status (for your AI pipeline)
    face_enrolled = models.BooleanField(default=False)

    # Multiple courses (as per your requirement)
    courses = models.ManyToManyField(Course, blank=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)  # Needed for admin panel

    created_at = models.DateTimeField(auto_now_add=True)

    objects = StudentManager()

    USERNAME_FIELD = 'admission_id'
    REQUIRED_FIELDS = ['dob']  # This fixes your error

    def __str__(self):
        return self.admission_id