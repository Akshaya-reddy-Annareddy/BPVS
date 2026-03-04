def sidebar_menu(request):

    if not request.user.is_authenticated:
        return {}

    role = request.user.role

    menus = {
        "admin": [
            {"name": "Profile", "url": "admin_profile"},
            {"name": "Courses", "url": "admin_courses"},
            {"name": "Subjects", "url": "admin_subjects"},
            {"name": "Lecturers", "url": "admin_lecturers"},
            {"name": "Timetable", "url": "admin_timetable"},  # ✅ added
            {"name": "Audit Logs", "url": "admin_audit_logs"},
            {"name": "Attendance Data", "url": "admin_attendance_data"},
        ],
        "student": [
            {"name": "Profile", "url": "student_profile"},
            {"name": "View Attendance", "url": "student_attendance"},
            {"name": "Classes", "url": "student_classes"},
            {"name": "Timetable", "url": "student_timetable"},  # ✅ added
            {"name": "Contact Admin", "url": "student_contact"},
        ],
        "lecturer": [
            {"name": "Profile", "url": "lecturer_profile"},
            {"name": "Classes", "url": "lecturer_classes"},
            {"name": "Timetable", "url": "lecturer_timetable"},  # ✅ added
            {"name": "Contact Admin", "url": "lecturer_contact"},
        ]
    }

    return {
        "sidebar_menu": menus.get(role, [])
    }