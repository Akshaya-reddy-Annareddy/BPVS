from django.urls import path
from .views import mark_attendance, attendance_page

urlpatterns = [
    path("", attendance_page), #handles /attendance/
    path("mark/", mark_attendance),
]