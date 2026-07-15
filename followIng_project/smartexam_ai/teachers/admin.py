from django.contrib import admin
from .models import Teacher, Resource, Course, Exam, Suggestion

@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ('user', 'department', 'designation')
    search_fields = ('user__username', 'user__email', 'department', 'designation')

@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    list_display = ('title', 'type', 'exam')
    list_filter = ('type',)
    search_fields = ('title', 'exam__title')

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_by', 'created_at')
    search_fields = ('title', 'created_by__username', 'created_by__email')

@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'exam_type', 'marks')
    list_filter = ('exam_type', 'course')
    search_fields = ('title', 'course__title')

@admin.register(Suggestion)
class SuggestionAdmin(admin.ModelAdmin):
    list_display = ('registered_course', 'is_ai_suggestion')
    list_filter = ('is_ai_suggestion',)
    search_fields = ('registered_course__student__user__username', 'registered_course__course__title')
