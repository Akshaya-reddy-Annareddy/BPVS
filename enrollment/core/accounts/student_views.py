from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import Count
from django.http import JsonResponse

from academics.models import Timetable, Subject
from attendance.models import AttendanceRecord, AttendanceSession
from accounts.models import Complaint
from .models import User
import requests
from django.views.decorators.csrf import csrf_exempt

def get_student_context(user):
    today = timezone.localdate()

    active_session = AttendanceSession.objects.filter(
        date=today,
        is_active=True,
        timetable__course=user.course,
        timetable__year=user.year
    ).exists()

    return {
        "active_session": active_session
    }

# -------------------------
# Student Dashboard
# -------------------------
@login_required
def student_dashboard(request):
    user = request.user

    if user.role != "student":
        return redirect("login")

    if not request.user.face_enrolled:
        return redirect("enrollment_instructions")
    
    today = timezone.localdate()
    current_day = today.strftime("%A")

    todays_classes = Timetable.objects.filter(
        course=user.course,
        year=user.year,
        day=current_day
    )

    total_attendance = AttendanceRecord.objects.filter(student=user).count()

    subjects = Subject.objects.filter(course=user.course, year=user.year)
    total_subjects = subjects.count()

    context = {
        "todays_classes": todays_classes,
        "total_attendance": total_attendance,
        "total_subjects": total_subjects,
        "face_enrolled": user.face_enrolled,
    }

    context.update(get_student_context(user))

    return render(request, "student/dashboard.html", context)


# -------------------------
# Student Profile
# -------------------------
@login_required
def student_profile(request):
    if request.user.role != "student":
        return redirect("login")
    context={}
    context.update(get_student_context(user))

    return render(request, "student/profile.html",context)


# -------------------------
# Student Attendance Page
# -------------------------
@login_required
def student_attendance(request):
    user = request.user

    if user.role != "student":
        return redirect("login")

    records = AttendanceRecord.objects.filter(student=user).select_related("subject")

    context = {
        "records": records
    }
    context.update(get_student_context(user))
    return render(request, "student/attendance.html", context)


# -------------------------
# Student Timetable
# -------------------------
@login_required
def student_timetable(request):
    user = request.user

    if user.role != "student":
        return redirect("login")

    timetable = Timetable.objects.filter(
        course=user.course,
        year=user.year
    )

    context = {}
    context.update(get_student_context(user))
    return render(request, "student/timetable.html", {"timetable": timetable},context)


# -------------------------
# Mark Attendance (API)
# -------------------------
@login_required
@csrf_exempt
def student_mark_attendance(request):
    if request.user.role != "student":
        return JsonResponse({"error": "Unauthorized"}, status=403)

    if request.method != "POST":
        return JsonResponse({"error": "Invalid method"}, status=400)

    today = timezone.localdate()

    active_session = AttendanceSession.objects.filter(
        date=today,
        is_active=True,
        timetable__course=request.user.course,
        timetable__year=request.user.year
    ).first()

    if not active_session:
        return JsonResponse({"error": "No active attendance session"}, status=400)

    # Prevent duplicate
    if AttendanceRecord.objects.filter(
        student=request.user,
        subject=active_session.timetable.subject,
        attendance_date=today
    ).exists():
        return JsonResponse({"error": "Already marked"}, status=400)

    try:
        # Forward frames to FastAPI
        files = request.FILES.getlist("files")

        response = requests.post(
            "http://localhost:8001/verify-face/",
            files=[("files", f) for f in files],
            timeout=15
        )

        result = response.json()

    except Exception as e:
        return JsonResponse({"error": "AI Server Offline"}, status=500)

    if result.get("status") == "success":
        AttendanceRecord.objects.create(
            student=request.user,
            subject=active_session.timetable.subject,
            lecturer=active_session.timetable.lecturer,
            course=request.user.course,
            attendance_date=today,
            status="Present"
        )

        return JsonResponse({"success": True})

    return JsonResponse(result, status=400)

# -------------------------
# Contact Admin
# -------------------------
@login_required
def student_contact_admin(request):
    if request.user.role != "student":
        return redirect("login")

    if request.method == "POST":
        Complaint.objects.create(
            student=request.user,
            subject=request.POST.get("subject"),
            message=request.POST.get("message")
        )
        return redirect("student_dashboard")
    context = {}
    context.update(get_student_context(user))
    return render(request, "student/contact.html", context)

@login_required
def student_classes(request):
    user = request.user

    if user.role != "student":
        return redirect("login")

    today = timezone.localdate()
    current_day = today.strftime("%A")

    todays_classes = Timetable.objects.filter(
        course=user.course,
        year=user.year,
        day=current_day
    )

    context = {
        "todays_classes": todays_classes,
    }

    context.update(get_student_context(user))

    return render(request, "student/classes.html", context)

@login_required
def student_enrollment_instructions(request):
    if request.user.face_enrolled:
        return redirect("student_dashboard")

    context = {}
    context.update(get_student_context(request.user))
    return render(request, "student/enrollment_instructions.html", context)