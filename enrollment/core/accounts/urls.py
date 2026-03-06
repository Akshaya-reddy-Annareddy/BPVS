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
from .student_views import *
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
    admin_add_course,
    admin_add_subject,
    admin_add_lecturer,

    # ADD THESE
    admin_edit_course,
    admin_delete_course,
    edit_subject,
    delete_subject,
    admin_edit_lecturer,
    admin_delete_lecturer,
    audit_log_detail,
    export_audit_logs,
    enrollment_instructions,
    enrollment_pipeline,
    signup_view,
)

urlpatterns = [

    # API ROUTES
    path("api/signup/", signup, name="api_signup"),
    path("api/login/", login_view, name="api_login"),
    path("api/mark-face-enrolled/", mark_face_enrolled, name="mark_face_enrolled"),
    path("api/check-enrollment/<str:admission_id>/", check_enrollment, name="check_enrollment"),

    #  WEB ROUTES 
    path("login/", login_view, name="login"),
    path("signup/", signup_view, name="signup"),
    path("logout/", LogoutView.as_view(next_page="login"), name="logout"),

    #  DASHBOARDS 
    path("admin/dashboard/", admin_dashboard, name="admin_dashboard"),
    path("student/dashboard/", student_dashboard, name="student_dashboard"),
    path("lecturer/dashboard/", lecturer_dashboard, name="lecturer_dashboard"),

    # ADMIN
    path("admin/profile/", admin_profile, name="admin_profile"),
    path("admin/courses/", admin_courses, name="admin_courses"),
    path("admin/subjects/", admin_subjects, name="admin_subjects"),
    path("admin/lecturers/", admin_lecturers, name="admin_lecturers"),
    path("admin/timetable/", admin_timetable, name="admin_timetable"),
    path("admin/audit-logs/", admin_audit_logs, name="admin_audit_logs"),
    path("admin/attendance-data/", admin_attendance_data, name="admin_attendance_data"),

    # ADD ACTIONS
    path("admin/add-course/", admin_add_course, name="admin_add_course"),
    path("admin/add-subject/", admin_add_subject, name="admin_add_subject"),
    path("admin/add-lecturer/", admin_add_lecturer, name="admin_add_lecturer"),
    path("admin/edit-course/<int:id>/", admin_edit_course, name="admin_edit_course"),

    # COURSE EDIT/DELETE
    path("admin/delete-course/<int:id>/", admin_delete_course, name="admin_delete_course"),

    # SUBJECT EDIT/DELETE
    path("admin/edit-subject/<int:id>/", edit_subject, name="edit_subject"),
    path("admin/delete-subject/<int:id>/", delete_subject, name="delete_subject"),

    # LECTURER EDIT/DELETE
    path("admin/edit-lecturer/<int:id>/", admin_edit_lecturer, name="admin_edit_lecturer"),
    path("admin/delete-lecturer/<int:id>/", admin_delete_lecturer, name="admin_delete_lecturer"),

    # AUDIT
    path("admin/audit-detail/<int:id>/", audit_log_detail, name="audit_log_detail"),
    path("admin/export-audit/", export_audit_logs, name="export_audit_logs"),

    # STUDENT
    path("student/dashboard/", student_dashboard, name="student_dashboard"),
    path("student/profile/", student_profile, name="student_profile"),
    path("student/attendance/", student_attendance, name="student_attendance"),
    path("student/timetable/", student_timetable, name="student_timetable"),
    path("student/mark-attendance/", student_mark_attendance, name="student_mark_attendance"),
    path("student/contact/", student_contact, name="student_contact"),
    path("student/classes/", student_classes, name="student_classes"),
    path("student/enroll/", student_enrollment_instructions, name="student_enrollment_instructions"),
    path("student/enrollment-pipeline/",enrollment_pipeline,name="enrollment_pipeline"),
    # LECTURER
    path("lecturer/profile/", lecturer_profile, name="lecturer_profile"),
    path("lecturer/classes/", lecturer_classes, name="lecturer_classes"),
    path("lecturer/timetable/", lecturer_timetable, name="lecturer_timetable"),
    path("lecturer/contact/", lecturer_contact, name="lecturer_contact"),
]