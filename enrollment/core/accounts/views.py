from django.shortcuts import render

from django.contrib.auth import get_user_model, authenticate
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from django.contrib.auth import login
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
import re
from academics.models import Course, Subject, Timetable, AuditLog
from attendance.models import AttendanceRecord
from django.utils import timezone
from .decorators import admin_required
from django.views.decorators.http import require_POST

from django.core.paginator import Paginator
from django.http import HttpResponse
import csv
from io import TextIOWrapper
from django.contrib import messages
from django.db.models import Count
from django.utils.timezone import now
from datetime import timedelta
from attendance.models import AttendanceSession
from datetime import date
from backend.services.vector_service import delete_embedding_by_admission
import requests

User = get_user_model()

@csrf_exempt
def signup(request):

    if request.method == "GET":
        return JsonResponse({"message": "Signup API is working. Use POST request."})

    if request.method != "POST":
        return JsonResponse({"error": "POST method required"}, status=400)

    try:
        data = json.loads(request.body)

        role = data.get("role")
        name = data.get("name")
        password = data.get("password")
        confirm_password = data.get("confirm_password")

        admission_id = data.get("admission_id")
        lecturer_id = data.get("lecturer_id")
        admin_id = data.get("admin_id")
        dob = data.get("dob")

        # Basic validation
        if not role or not name or not password or not confirm_password:
            return JsonResponse({"error": "All required fields must be filled"}, status=400)

        if password != confirm_password:
            return JsonResponse({"error": "Passwords do not match"}, status=400)

        # Strong password validation
        password_regex = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&]).{8,}$'
        if not re.match(password_regex, password):
            return JsonResponse({"error": "Weak password format"}, status=400)

        if role not in ["student", "lecturer", "admin"]:
            return JsonResponse({"error": "Invalid role"}, status=400)

        # ROLE LOGIC

        if role == "student":

            if not admission_id or not dob:
                return JsonResponse({"error": "Admission ID and DOB required"}, status=400)

            # AUTO UPPERCASE
            admission_id = admission_id.upper()

            admission_regex = r'^[0-9]{2}[A-Z]{3}[0-9]{4}$'
            if not re.match(admission_regex, admission_id):
                return JsonResponse({"error": "Invalid Admission ID format"}, status=400)

            if User.objects.filter(username=admission_id).exists():
                return JsonResponse({"error": "Admission ID already exists"}, status=400)

            user = User.objects.create_user(
                username=admission_id,
                password=password,
                role="student",
                admission_id=admission_id,
                first_name=name,
                dob=dob,
            )
            return redirect("student_dashboard")

        elif role == "lecturer":

            if not lecturer_id:
                return JsonResponse({"error": "Lecturer ID required"}, status=400)

            if User.objects.filter(username=lecturer_id).exists():
                return JsonResponse({"error": "Lecturer ID already exists"}, status=400)

            user = User.objects.create_user(
                username=lecturer_id,
                password=password,
                role="lecturer",
                lecturer_id=lecturer_id,
                first_name=name,
            )
            messages.success(request, "Lecturer registered suscessfully")
            return redirect("lecturer_dashboard")

        else:  # admin

            if not admin_id:
                return JsonResponse({"error": "Admin ID required"}, status=400)

            if User.objects.filter(username=admin_id).exists():
                return JsonResponse({"error": "Admin ID already exists"}, status=400)

            user = User.objects.create_user(
                username=admin_id,
                password=password,
                role="admin",
                admin_id=admin_id,
                first_name=name,
                is_staff=True,
                is_superuser=False
            )

        login(request, user)

        return JsonResponse({
            "message": "User created successfully",
            "redirect": f"/admin/dashboard/"
        })

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

@csrf_exempt
def login_view(request):

    #  API LOGIN (JSON) 
    if request.content_type == "application/json":
        try:
            data = json.loads(request.body)

            user_id = data.get("user_id")
            password = data.get("password")

            user = authenticate(username=user_id, password=password)

            if user is None:
                return JsonResponse({"error": "Invalid credentials"}, status=401)

            return JsonResponse({
                "message": "Login successful",
                "role": user.role,
                "face_enrolled": user.face_enrolled,
                "user_id": user.username
            })

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    #  DASHBOARD LOGIN (FORM) 
    if request.method == "POST":
        user_id = request.POST.get("user_id")
        password = request.POST.get("password")

        user = authenticate(request, username=user_id, password=password)

        if user is None:
            return render(request, "accounts/login.html", {
                "error": "Invalid credentials"
            })

        login(request, user)

        # ROLE BASED REDIRECT
        if user.role == "admin":
            return redirect("admin_dashboard")
        elif user.role == "student":
            return redirect("student_dashboard")
        elif user.role == "lecturer":
            return redirect("lecturer_dashboard")

    return render(request, "accounts/login.html")


@login_required
def mark_face_enrolled(request):

    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=400)

    try:
        user = request.user

        if user.role != "student":
            return JsonResponse({"error": "Invalid user"}, status=403)
        
        admission_id = user.admission_id

        data = json.loads(request.body)
        admission_id = data.get("admission_id")

        # Delete previous embeddings if re-enrolling
        if user.role == "student" and user.allow_reenroll:
            delete_embedding_by_admission(admission_id)

        # Update flags
        user.face_enrolled = True
        user.allow_reenroll = False
        user.re_enroll_used = True
        user.save()

        return JsonResponse({
            "message": "Face enrollment completed successfully"
        })

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
    


def check_enrollment(request, admission_id):
    try:
        user = User.objects.get(admission_id=admission_id)

        # Case 1: First time enrollment
        if not user.face_enrolled:
            return JsonResponse({
                "blocked": False,
                "allow_overwrite": False,
                "message": "First time enrollment allowed"
            })

        # Case 2: One-time re-enroll allowed
        elif not user.re_enroll_used:
            return JsonResponse({
                "blocked": False,
                "allow_overwrite": True,
                "message": "One-time re-enroll allowed"
            })

        # Case 3: Admin approved re-enroll
        elif user.admin_reenroll_allowed:
            return JsonResponse({
                "blocked": False,
                "allow_overwrite": True,
                "message": "Admin approved re-enroll"
            })

        # Case 4: Completely blocked
        else:
            return JsonResponse({
                "blocked": True,
                "allow_overwrite": False,
                "message": "Re-enrollment blocked. Contact admin."
            })

    except User.DoesNotExist:
        return JsonResponse({
            "blocked": True,
            "allow_overwrite": False,
            "message": "User not found"
        }, status=404)
    

#Dashborad views

@admin_required
def admin_dashboard(request):
    today = timezone.localdate()

    total_students = User.objects.filter(role="student").count()
    total_lecturers = User.objects.filter(role="lecturer").count()
    total_courses = Course.objects.count()
    today_attendance = AttendanceRecord.objects.filter(
        attendance_date=today
    ).count()
    
    print("ROLE:", request.user.role)
    return render(request, "admin/dashboard.html", {
        "total_students": total_students,
        "total_lecturers": total_lecturers,
        "total_courses": total_courses,
        "today_attendance": today_attendance,
    })


@login_required
def student_dashboard(request):

    if request.user.role != "student":
        return redirect("login")

    user = request.user
    today = date.today()

    # Total subjects
    total_subjects = Subject.objects.filter(course=user.course).count()

    # Total attendance
    total_attendance = AttendanceRecord.objects.filter(student=user).count()

    # Today's classes
    classes = Timetable.objects.filter(
        course=user.course,
        year=user.year,
        day=today.strftime("%A")
    )

    class_list = []
    active_session = False

    for cls in classes:

        active = AttendanceSession.objects.filter(
            timetable=cls,
            date=today,
            is_active=True
        ).exists()

        if active:
            active_session = True

        cls.session_active = active
        class_list.append(cls)

    return render(request, "student/dashboard.html", {
        "total_subjects": total_subjects,
        "total_attendance": total_attendance,
        "face_enrolled": user.face_enrolled,
        "todays_classes": class_list,
        "active_session": active_session
    })


@login_required
def lecturer_dashboard(request):
    if request.user.role != "lecturer":
        return redirect("login")
    return render(request, "lecturer/dashboard.html")

#  ADMIN 

@admin_required
def admin_profile(request):
    return render(request, "admin/profile.html")

@admin_required
def admin_courses(request):
    if request.user.role != "admin":
        return redirect("login")

    courses = Course.objects.all()

    return render(request, "admin/courses.html", {
        "courses": courses
    })

@admin_required
def admin_subjects(request):
    if request.user.role != "admin":
        return redirect("login")

    subjects = Subject.objects.select_related("course")

    return render(request, "admin/subjects.html", {
        "subjects": subjects
    })

@admin_required
def admin_lecturers(request):
    if request.user.role != "admin":
        return redirect("login")

    lecturers = User.objects.filter(role="lecturer")

    return render(request, "admin/lecturers.html", {
        "lecturers": lecturers
    })


@admin_required
def admin_timetable(request):

    if request.method == "POST" and request.FILES.get("csv_file"):
        csv_file = request.FILES["csv_file"]
        file_data = TextIOWrapper(csv_file.file, encoding="utf-8")
        reader = csv.DictReader(file_data)

        for row in reader:
            # Safe get or create
            course, _ = Course.objects.get_or_create(name=row["course"])
            subject, _ = Subject.objects.get_or_create(
                name=row["subject"],
                course=course
            )
            lecturer = User.objects.filter(
                lecturer_id=row["lecturer_id"],
                role="lecturer"
            ).first()

            if not lecturer:
                messages.error(request, f"Lecturer {row['lecturer_id']} not found")
                continue

            Timetable.objects.create(
                course=course,
                subject=subject,
                lecturer=lecturer,
                day=row["day"],
                start_time=row["start_time"],
                end_time=row["end_time"],
                room_number=row["room_number"]
            )

        messages.success(request, "Timetable uploaded successfully")
        return redirect("admin_timetable")

    timetables = Timetable.objects.select_related(
        "course", "subject", "lecturer"
    )

    return render(request, "admin/timetable.html", {
        "timetables": timetables
    })

@admin_required
def admin_audit_logs(request):

    logs = AuditLog.objects.all().order_by("-timestamp")

    # ================= FILTERS =================
    from_date = request.GET.get("from")
    to_date = request.GET.get("to")
    search = request.GET.get("search")

    if from_date:
        logs = logs.filter(timestamp__date__gte=from_date)

    if to_date:
        logs = logs.filter(timestamp__date__lte=to_date)

    if search:
        logs = logs.filter(
            admission_id__icontains=search
        ) | logs.filter(
            class_name__icontains=search
        ) | logs.filter(
            reason__icontains=search
        )

    # ================= PAGINATION =================
    paginator = Paginator(logs, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    # ================= STATS =================
    today = now().date()
    month_start = today.replace(day=1)

    today_count = AuditLog.objects.filter(timestamp__date=today).count()
    month_count = AuditLog.objects.filter(timestamp__date__gte=month_start).count()

    # Build cards directly (no stats dict needed)
    stats_cards = [
        ("Total Logs Today", today_count, "text-white"),
        ("This Month", month_count, "text-white"),
        ("Critical Events", 0, "text-red-400"),
        ("Failed Liveness", 0, "text-yellow-400"),
        ("Spoof Attempts", 0, "text-orange-400"),
        ("Manual Edits", 0, "text-blue-400"),
    ]

    return render(request, "admin/audit_logs.html", {
        "page_obj": page_obj,
        "stats_cards": stats_cards,
        "event_types": [],
        "severities": [],
        "roles": [],
    })

@admin_required
def admin_attendance_data(request):
    if request.user.role != "admin":
        return redirect("login")

    attendance = AttendanceRecord.objects.select_related(
        "student",
        "subject",
        "lecturer",
        "course"
    ).order_by("-attendance_date")

    return render(request, "admin/attendance_data.html", {
        "attendance": attendance
    })


@admin_required
@require_POST
def admin_add_course(request):
    name = request.POST.get("name")
    if name:
        Course.objects.create(name=name)
    return redirect("admin_courses")


@admin_required
@require_POST
def admin_add_subject(request):
    name = request.POST.get("name")
    course_id = request.POST.get("course_id")

    if name and course_id:
        course = Course.objects.get(id=course_id)
        Subject.objects.create(name=name, course=course)

    return redirect("admin_subjects")


@admin_required
@require_POST
def admin_add_lecturer(request):
    lecturer_id = request.POST.get("lecturer_id")
    name = request.POST.get("name")
    password = request.POST.get("password")

    if lecturer_id and password:
        User.objects.create_user(
            username=lecturer_id,
            password=password,
            role="lecturer",
            lecturer_id=lecturer_id,
            first_name=name
        )

    return redirect("admin_lecturers")

@admin_required
def admin_edit_course(request, id):
    course = Course.objects.get(id=id)

    if request.method == "POST":
        course.name = request.POST.get("name")
        course.duration = request.POST.get("duration")
        course.semesters = request.POST.get("semesters")
        course.save()
        return redirect("admin_courses")

    return render(request, "admin/edit_course.html", {"course": course})


@admin_required
def admin_delete_course(request, id):
    course = Course.objects.get(id=id)
    course.delete()
    return redirect("admin_courses")

@admin_required
def edit_subject(request, id):
    subject = Subject.objects.get(id=id)

    if request.method == "POST":
        subject.name = request.POST.get("name")
        subject.semester = request.POST.get("semester")
        subject.credits = request.POST.get("credits")
        subject.status = request.POST.get("status")
        subject.save()
        return redirect("admin_subjects")

    return render(request, "admin/edit_subject.html", {"subject": subject})


@admin_required
def delete_subject(request, id):
    subject = Subject.objects.get(id=id)
    subject.delete()
    return redirect("admin_subjects")

@admin_required
def admin_edit_lecturer(request, id):
    lecturer = User.objects.get(id=id, role="lecturer")

    if request.method == "POST":
        lecturer.first_name = request.POST.get("name")
        lecturer.save()
        return redirect("admin_lecturers")

    return render(request, "admin/edit_lecturer.html", {"lecturer": lecturer})


@admin_required
def admin_delete_lecturer(request, id):
    lecturer = User.objects.get(id=id, role="lecturer")
    lecturer.delete()
    return redirect("admin_lecturers")

@admin_required
def audit_log_detail(request, id):
    log = AuditLog.objects.get(id=id)
    return render(request, "admin/audit_detail.html", {"log": log})


@admin_required
def export_audit_logs(request):
    logs = AuditLog.objects.all()

    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="audit_logs.csv"'

    writer = csv.writer(response)
    writer.writerow(["Event ID", "Type", "Actor", "Role", "Severity", "Timestamp"])

    for log in logs:
        writer.writerow([
            log.event_id,
            log.event_type,
            log.actor_name,
            log.actor_role,
            log.severity,
            log.timestamp
        ])

    return response
#  STUDENT 

@login_required
def student_profile(request):
    return render(request, "student/profile.html")

@login_required
def student_attendance(request):

    user = request.user

    attendance_records = AttendanceRecord.objects.filter(
        student=user
    ).order_by("_attendance_date")

    total_classes = attendance_records.count()

    present_count = attendance_records.filter(status="P").count()

    attendance_percentage = 0

    if total_classes > 0:
        attendance_percentage = round((present_count / total_classes) * 100, 2)

    context = {
        "attendance_records": attendance_records,
        "total_classes": total_classes,
        "present_count": present_count,
        "attendance_percentage": attendance_percentage
    }

    return render(request, "student/view_attendance.html", context)

@login_required
def student_classes(request):

    user = request.user
    today = date.today()

    classes = Timetable.objects.filter(
        course=user.course,
        year=user.year,
        day=today.strftime("%A")
    )

    class_list = []

    for cls in classes:

        active = AttendanceSession.objects.filter(
            timetable=cls,
            date=today,
            is_active=True
        ).exists()

        cls.session_active = active
        class_list.append(cls)

    return render(
        request,
        "student/classes.html",
        {"todays_classes": class_list}
    )

@login_required
def student_timetable(request):
    return render(request, "student/timetable.html")

@login_required
def student_contact(request):
    return render(request, "student/contact.html")

@login_required
def enrollment_instructions(request):

    user = request.user

    # If student is re-enrolling
    if user.role == "student" and user.allow_reenroll:

        # Delete old face embedding from Qdrant
        delete_embedding_by_admission(request.user.admission_id)

        # Reset enrollment state
        user.face_enrolled = False
        user.allow_reenroll = False
        user.save()

    return render(request, "enrollment/instructions.html")

@login_required
def enrollment_pipeline(request):
    return render(request, "index.html")

# LECTURER 

@login_required
def lecturer_profile(request):
    return render(request, "lecturer/profile.html")

@login_required
def lecturer_classes(request):
    return render(request, "lecturer/classes.html")

@login_required
def lecturer_timetable(request):
    return render(request, "lecturer/timetable.html")

@login_required
def lecturer_contact(request):
    return render(request, "lecturer/contact_admin.html")

def signup_view(request):

    if request.method == "POST":

        name = request.POST.get("name")
        admission_id = request.POST.get("admission_id")
        password = request.POST.get("password")
        dob = request.POST.get("dob")

        if not admission_id or not password:
            messages.error(request, "Admission ID and Password required")
            return redirect("signup")

        admission_id = admission_id.upper()

        user = User.objects.create_user(
            username=admission_id,
            password=password,
            role="student",
            admission_id=admission_id,
            first_name=name,
            dob=dob
        )

        login(request, user)

        messages.success(request, "Registered successfully")

        return redirect("enrollment_page")

    return redirect("/auth/")

"""
def signup_view(request):

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = User.objects.create_user(
            username=username,
            password=password
        )

        login(request, user)

        return redirect("enrollment_page")

    return redirect("/auth/")
"""
    
def delete_face_embedding(admission_id):

    response = requests.post(
        "http://localhost:8001/delete-embedding",
        json={"admission_id": admission_id}
    )

    return response.json()