from django.contrib import admin
from .models import Student, RegisteredCourse, AnswerScript, Review

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('user', 'university', 'department')
    search_fields = ('user__username', 'user__email', 'university', 'department')

@admin.register(RegisteredCourse)
class RegisteredCourseAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'enrolled_at')
    list_filter = ('course',)
    search_fields = ('student__user__username', 'course__title')

@admin.register(AnswerScript)
class AnswerScriptAdmin(admin.ModelAdmin):
    list_display = ('registered_course', 'exam', 'marks', 'is_evaluated')
    list_filter = ('is_evaluated', 'exam')
    search_fields = ('registered_course__student__user__username', 'exam__title')

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('registered_course', 'rating')
    list_filter = ('rating',)
    search_fields = ('registered_course__course__title', 'registered_course__student__user__username')
