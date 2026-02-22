from django.http import HttpResponse
import os
from django.conf import settings


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
    file_path = os.path.join(PROJECT_ROOT, "frontend", "attendance.html")
    with open(file_path, "r", encoding="utf-8") as f:
        return HttpResponse(f.read())