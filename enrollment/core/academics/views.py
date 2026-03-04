from django.shortcuts import render

from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from .models import AuditLog
import json
from django.contrib.auth.decorators import login_required
from .models import Course


@csrf_exempt
def spoof_log(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=400)

    try:
        data = json.loads(request.body)

        AuditLog.objects.create(
            admission_id=data.get("admission_id"),
            reason=data.get("reason"),
            timestamp=data.get("timestamp"),
            course=data.get("course"),
            class_name=data.get("class_name"),
        )

        return JsonResponse({"message": "Audit log stored"})

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@login_required
def courses_page(request):
    return render(request, "admin/courses.html")


@login_required
def get_courses(request):
    courses = Course.objects.all().values()
    return JsonResponse(list(courses), safe=False)


@csrf_exempt
@login_required
def create_course(request):
    if request.method == "POST":
        data = json.loads(request.body)

        course = Course.objects.create(
            name=data["name"],
            code=data["code"],
            duration_years=data["duration_years"],
        )

        return JsonResponse({"message": "Course created"})


@csrf_exempt
@login_required
def update_course(request, course_id):
    if request.method == "PUT":
        data = json.loads(request.body)

        course = Course.objects.get(id=course_id)
        course.name = data["name"]
        course.code = data["code"]
        course.duration_years = data["duration_years"]
        course.save()

        return JsonResponse({"message": "Course updated"})


@csrf_exempt
@login_required
def delete_course(request, course_id):
    if request.method == "DELETE":
        Course.objects.get(id=course_id).delete()
        return JsonResponse({"message": "Course deleted"})