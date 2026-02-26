from django.shortcuts import render

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import AttendanceRecord
from datetime import datetime
from django.utils import timezone
import json
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

def calculate_year(admission_id):
    try:
        admission_year = int("20" + admission_id[:2])  # 23 -> 2023
        current_year = datetime.now().year
        year = current_year - admission_year + 1
        return min(max(year, 1), 4)
    except:
        return 1


def get_course_code(admission_id):
    return admission_id[2:5]  # 23CAM1001 -> CAM

def attendance_page(request):
    return render(request, "attendance/attendance.html")

@csrf_exempt
def mark_attendance(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=400)

    try:
        data = json.loads(request.body)

        admission_id = data.get("admission_id")
        subject_name = data.get("subject_name")
        lecturer_id = data.get("lecturer_id")

        if not admission_id or not subject_name or not lecturer_id:
            return JsonResponse({"error": "Missing fields"}, status=400)

        today = timezone.localdate() #IST date

        #Check: Already marked today?
        already_marked = AttendanceRecord.objects.filter(
            admission_id = admission_id,
            subject_name = subject_name,
            attendance_date=today
        ).exists()

        if already_marked:
            return JsonResponse({
                "message": "Attendance already marked for this subject today",
                "status" : "duplicate_blocked"
            }, status=200)

        #Auto extract academic details       
        course_code = get_course_code(admission_id)
        year = calculate_year(admission_id)

        AttendanceRecord.objects.create(
            admission_id=admission_id,
            course_code=course_code,
            year=year,
            subject_name=subject_name,
            lecturer_id=lecturer_id,
            attendance_date=today,
            status="Present"
        )

        return JsonResponse({
            "message": "Attendance stored successfully",
            "course": course_code,
            "year": year,
            "date": str(today)
        })

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

