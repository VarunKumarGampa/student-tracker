from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    # Fields shown in the user list view
    list_display  = ('email', 'username', 'role', 'is_staff', 'is_active')
    list_filter   = ('role', 'is_staff', 'is_active')
    search_fields = ('email', 'username')
    ordering      = ('email',)

    # Add our custom fields to the admin edit form
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Student Tracker Info', {
            'fields': ('role', 'grade', 'subject')
        }),
    )