from django.urls import path

from .views import (
    spoof_log,
    courses_page,
    get_courses,
    create_course,
    update_course,
    delete_course,
)

urlpatterns = [
    path("spoof-log/", spoof_log),
    path("dashboard/admin/courses/", courses_page, name="courses_page"),
    path("api/courses/", get_courses),
    path("api/courses/create/", create_course),
    path("api/courses/<int:course_id>/update/", update_course),
    path("api/courses/<int:course_id>/delete/", delete_course),
]