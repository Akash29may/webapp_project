from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('is_teacher', 'is_student', 'contact_no', 'profile_img', 'bio')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Additional Info', {'fields': ('is_teacher', 'is_student', 'contact_no', 'profile_img', 'bio')}),
    )
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_teacher', 'is_student', 'is_staff')
    list_filter = ('is_teacher', 'is_student', 'is_staff', 'is_superuser', 'is_active')
    search_fields = ('username', 'first_name', 'last_name', 'email')

admin.site.register(User, CustomUserAdmin)
