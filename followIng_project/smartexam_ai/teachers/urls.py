from django.urls import path
from . import views

app_name = 'teachers'

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('create_course/', views.create_course, name='create_course'),
    path('courses/', views.course_list, name='courses'),
    path('courses/<int:course_id>/', views.course_detail, name='course_detail'),
    path('courses/<int:course_id>/edit/', views.edit_course, name='edit_course'),
    path('courses/<int:course_id>/add-exam/', views.add_exam, name='add_exam'),
    path('exams/', views.exam_list, name='exams'),
    path('exams/<int:exam_id>/', views.exam_detail, name='exam_detail'),
    path('exams/<int:exam_id>/edit/', views.edit_exam, name='edit_exam'),
    path('students/<int:student_id>/', views.student_detail, name='student_detail'),
    path('ai_gen_questions/', views.ai_gen_qs, name='ai_gen_qs'),
    path('evaluate/', views.evaluate, name='evaluate'),
]
