from django.db import models
from django.conf import settings
from django.utils import timezone
from academics.models import Subject, Course, Timetable

class AttendanceRecord(models.Model):

    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'student'}
    )

    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)

    lecturer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="lecturer_attendance",
        limit_choices_to={'role': 'lecturer'}
    )

    course = models.ForeignKey(Course, on_delete=models.CASCADE)

    attendance_date = models.DateField(default=timezone.localdate)
    timestamp = models.DateTimeField(default=timezone.now)

    status = models.CharField(
        max_length=10,
        choices=[
            ("Present", "Present"),
            ("Absent", "Absent"),
        ],
        default="Present"
    )

    class Meta:
        unique_together = ("student", "subject", "attendance_date")

        indexes = [
            models.Index(fields=["student"]),
            models.Index(fields=["attendance_date"]),
            models.Index(fields=["subject"]),
        ]

    def __str__(self):
        return f"{self.student.username} - {self.subject.name} - {self.attendance_date}"
    
def get_attendance_percentage(student, subject):
    total_classes = Timetable.objects.filter(
        subject=subject,
        course=student.course
    ).count()

    attended = AttendanceRecord.objects.filter(
        student=student,
        subject=subject
    ).count()

    if total_classes == 0:
        return 0

    return round((attended / total_classes) * 100, 2)

class AttendanceSession(models.Model):
    timetable = models.ForeignKey(Timetable, on_delete=models.CASCADE)
    date = models.DateField()
    is_active = models.BooleanField(default=False)
    started_at = models.DateTimeField(null=True, blank=True)
    ended_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.timetable} - {self.date}"

class Complaint(models.Model):
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'student'}
    )
    subject = models.CharField(max_length=200)
    message = models.TextField()
    status = models.CharField(
        max_length=20,
        choices=[
            ("pending", "Pending"),
            ("resolved", "Resolved"),
        ],
        default="pending"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.username} - {self.subject}"