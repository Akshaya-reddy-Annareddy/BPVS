from django.urls import path
from .views import *

urlpatterns = [
    path("", attendance_page, name="attendance_pipeline"), #handles /attendance/
    path("mark/", mark_attendance, name="mark_attendance"),
    path("attendance/count/<int:timetable_id>/",attendance_count,name="attendance_count"),
    path("sheet/<int:timetable_id>/",attendance_sheet,name="attendance_sheet"),
    path("toggle/<int:record_id>/",toggle_attendance,name="toggle_attendance"),
]