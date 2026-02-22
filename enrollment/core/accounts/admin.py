from django.contrib import admin
from .models import User

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("id", "role", "is_active", "is_staff")
    search_fields = ("id",)
    list_filter = ("role", "is_active", "is_staff")