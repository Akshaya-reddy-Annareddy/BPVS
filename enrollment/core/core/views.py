from django.http import HttpResponse
import os
from django.conf import settings
from django.contrib.auth import get_user_model

User = get_user_model()

# Correct root folder (enrollment/)
PROJECT_ROOT = os.path.dirname(settings.BASE_DIR)


def home(request):
    file_path = os.path.join(PROJECT_ROOT, "frontend", "index.html")
    with open(file_path, "r", encoding="utf-8") as f:
        return HttpResponse(f.read())


def auth_page(request):
    file_path = os.path.join(PROJECT_ROOT, "frontend", "auth.html")
    with open(file_path, "r", encoding="utf-8") as f:
        return HttpResponse(f.read())


def attendance_page(request):
    # STEP 3 SECURITY CHECK (MANDATORY)
    user_id = request.GET.get("user_id")

    if not user_id:
        return HttpResponse("Unauthorized access. Please login first.", status=403)

    try:
        user = User.objects.get(username=user_id)

        # Block if face not enrolled
        if user.role == "student" and not user.face_enrolled:
            return HttpResponse(
                "Face enrollment required before accessing attendance.",
                status=403
            )

    except User.DoesNotExist:
        return HttpResponse("User not found", status=404)

    # If passed all checks → load attendance page
    file_path = os.path.join(PROJECT_ROOT, "frontend", "attendance.html")
    with open(file_path, "r", encoding="utf-8") as f:
        return HttpResponse(f.read())