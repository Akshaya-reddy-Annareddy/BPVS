from django.urls import path
from .views import mark_attendance, attendance_page

urlpatterns = [
    path("", attendance_page, name="attendance_pipeline"), #handles /attendance/
    path("mark/", mark_attendance, name="mark_attendance"),
]