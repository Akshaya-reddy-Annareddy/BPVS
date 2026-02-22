from django.shortcuts import render

from django.contrib.auth import get_user_model, authenticate
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

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
        dob = data.get("dob")

        admission_id = data.get("admission_id")
        lecturer_id = data.get("lecturer_id")
        admin_id = data.get("admin_id")

        if role not in ["student", "lecturer", "admin"]:
            return JsonResponse({"error": "Invalid role"}, status=400)

        if not password or not name:
            return JsonResponse({"error": "Name and password required"}, status=400)

        if role == "student":
            if not admission_id or not dob:
                return JsonResponse({"error": "Admission ID and DOB required"}, status=400)

            user = User.objects.create_user(
                username=admission_id,
                password=password,
                role="student",
                admission_id=admission_id,
                first_name=name,
                dob=dob,
            )

        elif role == "lecturer":
            if not lecturer_id:
                return JsonResponse({"error": "Lecturer ID required"}, status=400)

            user = User.objects.create_user(
                username=lecturer_id,
                password=password,
                role="lecturer",
                lecturer_id=lecturer_id,
                first_name=name,
            )

        else:  # admin
            if not admin_id:
                return JsonResponse({"error": "Admin ID required"}, status=400)

            user = User.objects.create_user(
                username=admin_id,
                password=password,
                role="admin",
                admin_id=admin_id,
                first_name=name,
                is_staff=True,
                is_superuser=False
            )

        return JsonResponse({"message": "User created successfully"})

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
def login_view(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST method required"}, status=400)

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
