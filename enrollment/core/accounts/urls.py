"""
from django.urls import path
from .views import signup, login_view, mark_face_enrolled, check_enrollment

urlpatterns = [
    path("signup/", signup),
    path("login/", login_view),
    path("mark-face-enrolled/", mark_face_enrolled),
    path("check-enrollment/<str:admission_id>/", check_enrollment),
]

"""

from django.urls import path
from django.contrib.auth.views import LogoutView
from .views import (
    signup,
    login_view,
    mark_face_enrolled,
    check_enrollment,
    admin_dashboard,
    student_dashboard,
    lecturer_dashboard,
    admin_profile,
    admin_attendance_data,
    admin_audit_logs,
    admin_courses,
    admin_lecturers,
    admin_subjects,
    admin_timetable,
    student_attendance,
    student_classes,
    student_contact,
    student_profile,
    student_timetable,
    lecturer_classes,
    lecturer_contact,
    lecturer_profile,
    lecturer_timetable,
    
)

urlpatterns = [

    # API ROUTES
    path("api/signup/", signup, name="api_signup"),
    path("api/login/", login_view, name="api_login"),
    path("api/mark-face-enrolled/", mark_face_enrolled, name="mark_face_enrolled"),
    path("api/check-enrollment/<str:admission_id>/", check_enrollment, name="check_enrollment"),

    #  WEB ROUTES 
    path("login/", login_view, name="login"),
    path("logout/", LogoutView.as_view(next_page="login"), name="logout"),

    #  DASHBOARDS 
    path("admin-dashboard/", admin_dashboard, name="admin_dashboard"),
    path("student-dashboard/", student_dashboard, name="student_dashboard"),
    path("lecturer-dashboard/", lecturer_dashboard, name="lecturer_dashboard"),

    # ADMIN
    path("admin/profile/", admin_profile, name="admin_profile"),
    path("admin/courses/", admin_courses, name="admin_courses"),
    path("admin/subjects/", admin_subjects, name="admin_subjects"),
    path("admin/lecturers/", admin_lecturers, name="admin_lecturers"),
    path("admin/timetable/", admin_timetable, name="admin_timetable"),
    path("admin/audit-logs/", admin_audit_logs, name="admin_audit_logs"),
    path("admin/attendance-data/", admin_attendance_data, name="admin_attendance_data"),

    # STUDENT
    path("student/profile/", student_profile, name="student_profile"),
    path("student/attendance/", student_attendance, name="student_attendance"),
    path("student/classes/", student_classes, name="student_classes"),
    path("student/timetable/", student_timetable, name="student_timetable"),
    path("student/contact/", student_contact, name="student_contact"),

    # LECTURER
    path("lecturer/profile/", lecturer_profile, name="lecturer_profile"),
    path("lecturer/classes/", lecturer_classes, name="lecturer_classes"),
    path("lecturer/timetable/", lecturer_timetable, name="lecturer_timetable"),
    path("lecturer/contact/", lecturer_contact, name="lecturer_contact"),
]