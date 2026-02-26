from django.urls import path
from .views import signup, login_view, mark_face_enrolled, check_enrollment

urlpatterns = [
    path("signup/", signup),
    path("login/", login_view),
    path("mark-face-enrolled/", mark_face_enrolled),
    path("check-enrollment/<str:admission_id>/", check_enrollment),
]