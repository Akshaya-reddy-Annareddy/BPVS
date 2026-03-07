from django.shortcuts import render
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import AttendanceRecord, AttendanceSession
from datetime import datetime
from django.utils import timezone
import json
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from academics.models import Subject, Course, Timetable, AuditLog
from accounts.models import User
from datetime import datetime
import pytz


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

def mark_attendance(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=400)

    try:
        data = json.loads(request.body)
        admission_id = data.get("admission_id")

        if not admission_id:
            return JsonResponse({"error": "Admission ID missing"}, status=400)

        # Get student
        student = User.objects.get(admission_id=admission_id, role="student")

        # Get current IST time
        ist = pytz.timezone("Asia/Kolkata")
        now = datetime.now(ist)

        current_day = now.strftime("%A")  # Monday, Tuesday...
        current_time = now.time()
        today = now.date()

        # Find active class from timetable
        active_class = Timetable.objects.filter(
            course=student.course,
            day=current_day,
            start_time__lte=current_time,
            end_time__gte=current_time
        ).select_related("subject", "lecturer", "course").first()

        if not active_class:
            return JsonResponse({
                "status": "no_class",
                "message": "No active class right now"
            })

        # Check duplicate attendance
        if AttendanceRecord.objects.filter(
            student=student,
            subject=active_class.subject,
            attendance_date=today
        ).exists():
            return JsonResponse({
                "status": "duplicate",
                "message": "Attendance already marked"
            })

        # Create attendance
        AttendanceRecord.objects.create(
            student=student,
            subject=active_class.subject,
            lecturer=active_class.lecturer,
            course=active_class.course,
            attendance_date=today
        )

        return JsonResponse({
            "status": "success",
            "message": f"Attendance marked for {active_class.subject.name}"
        })

    except User.DoesNotExist:
        return JsonResponse({"error": "Student not found"}, status=404)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


def attendance_count(request, timetable_id):

    timetable = Timetable.objects.get(id=timetable_id)

    today = timezone.localdate()

    session = AttendanceSession.objects.filter(
        timetable=timetable,
        date=today,
        is_active=True
    ).first()

    if session:
        if timezone.now() > session.ended_at:
            session.is_active = False
            session.save()

    count = AttendanceRecord.objects.filter(
        subject=timetable.subject,
        course=timetable.course,
        attendance_date=today
    ).count()

    return JsonResponse({
        "count": count
    })


def attendance_sheet(request, timetable_id):

    timetable = get_object_or_404(Timetable, id=timetable_id)

    today = timezone.localdate()

    records = AttendanceRecord.objects.filter(
        subject=timetable.subject,
        course=timetable.course,
        attendance_date=today
    ).select_related("student")

    context = {
        "records": records,
        "timetable": timetable
    }

    return render(request, "lecturer/attendance_sheet.html", context)

def toggle_attendance(request, record_id):

    record = get_object_or_404(AttendanceRecord, id=record_id)

    if record.status == "present":
        record.status = "absent"
    else:
        record.status = "present"

    record.save()

    # create audit log
    AuditLog.objects.create(
        admission_id=record.student.admission_id,
        reason=f"Manual attendance edit by lecturer {request.user.username}",
        timestamp=timezone.now(),
        course=record.course.code,
        class_name=record.subject.name
    )

    return redirect(
        "attendance_sheet",
        timetable_id=request.GET.get("timetable")
    )