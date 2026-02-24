from django.db import models
from django.utils import timezone


class AttendanceRecord(models.Model):
    admission_id = models.CharField(max_length=50, db_index=True)
    course_code = models.CharField(max_length=10)
    year = models.IntegerField()
    subject_name = models.CharField(max_length=100)
    lecturer_id = models.CharField(max_length=50)

    # IMPORTANT: Separate date field for uniqueness logic
    attendance_date = models.DateField(default=timezone.now)

    timestamp = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=10, default="Present")

    class Meta:
        # THIS LINE PREVENTS DUPLICATE ATTENDANCE (DATABASE LEVEL)
        unique_together = ("admission_id", "subject_name", "attendance_date")

        indexes = [
            models.Index(fields=["admission_id"]),
            models.Index(fields=["attendance_date"]),
            models.Index(fields=["subject_name"]),
        ]

    def __str__(self):
        return f"{self.admission_id} - {self.subject_name} - {self.attendance_date}"