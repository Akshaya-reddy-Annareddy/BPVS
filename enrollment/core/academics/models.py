from django.db import models

from django.conf import settings

#Course model
class Course(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10, unique=True)  # CAM, CSE, ECE etc.
    duration_years = models.IntegerField(default=4)

    def __str__(self):
        return f"{self.name} ({self.code})"

#Subject model   
class Subject(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    year = models.IntegerField()  # 1,2,3,4

    def __str__(self):
        return f"{self.name} - Year {self.year}"
    
#Timetable model
class Timetable(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    year = models.IntegerField()
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    lecturer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'lecturer'}
    )

    day = models.CharField(max_length=20)
    start_time = models.TimeField()
    end_time = models.TimeField()

    def __str__(self):
        return f"{self.course.code} Y{self.year} - {self.subject.name} - {self.day}"
    
#Audit log model
class AuditLog(models.Model):
    admission_id = models.CharField(max_length=50)
    reason = models.TextField()
    timestamp = models.DateTimeField()
    course = models.CharField(max_length=50)
    class_name = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.admission_id} - {self.reason}"

