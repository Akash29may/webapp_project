from django.urls import path
from . import views

app_name = 'students'

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('courses/', views.browse_courses, name='browse_courses'),
    path('courses/<int:course_id>/', views.course_detail, name='course_detail'),
    path('courses/<int:course_id>/enroll/', views.enroll_course, name='enroll_course'),
    path('exams/', views.exams_list, name='exams_list'),
    path('exams/<int:exam_id>/', views.exam_detail, name='exam_detail'),
    path('exams/<int:exam_id>/take/', views.take_exam, name='take_exam'),
    path('exams/<int:exam_id>/script/', views.answer_script, name='answer_script'),
]
