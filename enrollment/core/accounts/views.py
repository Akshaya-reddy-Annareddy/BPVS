from django.shortcuts import render

from django.contrib.auth import get_user_model, authenticate
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .models import User
from django.contrib.auth import login
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
import re

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
            return redirect("student/dashboard")

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
            return redirect("lecturer/dashboard")

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
            "redirect": f"/{role}/dashboard/"
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
            return redirect("/admin/dashboard/")
        elif user.role == "student":
            return redirect("/student/dashboard/")
        elif user.role == "lecturer":
            return redirect("/lecturer/dashboard/")

    return render(request, "accounts/login.html")

@csrf_exempt
def mark_face_enrolled(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=400)

    try:
        data = json.loads(request.body)
        admission_id = data.get("admission_id")

        if not admission_id:
            return JsonResponse({"error": "Admission ID required"}, status=400)

        user = User.objects.filter(admission_id=admission_id, role="student").first()

        if not user:
            return JsonResponse({"error": "Student not found"}, status=404)

        user.face_enrolled = True
        user.save()

        return JsonResponse({"message": "Face enrollment status updated"})

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

@login_required
def admin_dashboard(request):
    if request.user.role != "admin":
        return redirect("login")
    return render(request, "admin/dashboard.html")


@login_required
def student_dashboard(request):
    if request.user.role != "student":
        return redirect("login")
    return render(request, "student/dashboard.html")


@login_required
def lecturer_dashboard(request):
    if request.user.role != "lecturer":
        return redirect("login")
    return render(request, "lecturer/dashboard.html")

#  ADMIN 

@login_required
def admin_profile(request):
    return render(request, "admin/profile.html")

@login_required
def admin_courses(request):
    return render(request, "admin/courses.html")

@login_required
def admin_subjects(request):
    return render(request, "admin/subjects.html")

@login_required
def admin_lecturers(request):
    return render(request, "admin/lecturers.html")

@login_required
def admin_timetable(request):
    return render(request, "admin/timetable.html")

@login_required
def admin_audit_logs(request):
    return render(request, "admin/audit_logs.html")

@login_required
def admin_attendance_data(request):
    return render(request, "admin/attendance_data.html")


#  STUDENT 

@login_required
def student_profile(request):
    return render(request, "student/profile.html")

@login_required
def student_attendance(request):
    return render(request, "student/attendance.html")

@login_required
def student_classes(request):
    return render(request, "student/classes.html")

@login_required
def student_timetable(request):
    return render(request, "student/timetable.html")

@login_required
def student_contact(request):
    return render(request, "student/contact.html")


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
    return render(request, "lecturer/contact.html")