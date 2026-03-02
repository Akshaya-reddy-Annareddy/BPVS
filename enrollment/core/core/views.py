from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.http import HttpResponse

User = get_user_model()


# HOME PAGE
def home(request):
    return render(request, "index.html")



# AUTH PAGE
def auth_page(request):
    return render(request, "auth/auth.html")



# ATTENDANCE PAGE
@login_required
def attendance_page(request):

    user = request.user

    # Block if student and face not enrolled
    if user.role == "student" and not user.face_enrolled:
        return HttpResponse(
            "Face enrollment required before accessing attendance.",
            status=403
        )

    return render(request, "attendance/attendance.html")