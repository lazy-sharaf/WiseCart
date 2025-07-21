from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

# Customize the UserAdmin class to display additional fields
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ['username', 'full_name', 'email', 'gender', 'user_type', 'is_staff', 'is_active']
    search_fields = ['username', 'email', 'full_name']
    list_filter = ['user_type', 'is_staff', 'is_active', 'gender']
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('full_name', 'gender', 'user_type')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('full_name', 'gender', 'user_type')}),
    )
    ordering = ['username']

# Register the CustomUser model with the CustomUserAdmin class
admin.site.register(CustomUser, CustomUserAdmin)
