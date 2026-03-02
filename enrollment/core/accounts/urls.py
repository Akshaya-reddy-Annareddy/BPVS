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
from .views import (
    signup,
    login_view,
    mark_face_enrolled,
    check_enrollment,
    admin_dashboard,
    student_dashboard,
    lecturer_dashboard
)

urlpatterns = [

    # API ROUTES
    path("api/signup/", signup, name="api_signup"),
    path("api/login/", login_view, name="api_login"),
    path("api/mark-face-enrolled/", mark_face_enrolled, name="mark_face_enrolled"),
    path("api/check-enrollment/<str:admission_id>/", check_enrollment, name="check_enrollment"),

    #  WEB ROUTES 
    path("login/", login_view, name="login"),

    #  DASHBOARDS 
    path("admin-dashboard/", admin_dashboard, name="admin_dashboard"),
    path("student-dashboard/", student_dashboard, name="student_dashboard"),
    path("lecturer-dashboard/", lecturer_dashboard, name="lecturer_dashboard"),
]