from django.contrib import admin

from .models import Answer, Choice, Exam, ExamAttempt, Question


class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 4


class QuestionInline(admin.StackedInline):
    model = Question
    extra = 0


@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ("title", "teacher", "duration_min", "is_published", "created_at")
    inlines = [QuestionInline]


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ("text", "exam", "qtype", "marks", "difficulty")
    inlines = [ChoiceInline]


admin.site.register(ExamAttempt)
admin.site.register(Answer)
