from django.contrib import admin
from .models import User

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("user_id", "name", "role", "is_active", "is_staff")
    search_fields = ("user_id", "name")
    list_filter = ("role", "is_active", "is_staff")