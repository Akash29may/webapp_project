from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from .models import Course, Exam, Resource
from students.models import RegisteredCourse, AnswerScript, Student
import json

# Create your views here.

@login_required
def dashboard(request):
    user = request.user
    
    # Calculate stats
    total_courses = Course.objects.filter(created_by=user).count()
    total_exams = Exam.objects.filter(course__created_by=user).count()
    total_students = RegisteredCourse.objects.filter(course__created_by=user).values('student').distinct().count()
    
    # Recent courses
    recent_courses = Course.objects.filter(created_by=user).order_by('-created_at')[:5]
    
    # Recent submissions
    recent_submissions = AnswerScript.objects.filter(exam__course__created_by=user).order_by('-id')[:5]
    
    context = {
        'total_courses': total_courses,
        'total_exams': total_exams,
        'total_students': total_students,
        'recent_courses': recent_courses,
        'recent_submissions': recent_submissions,
    }
    
    return render(request, "teachers/dashboard.html", context)

@login_required
def create_course(request):
    if request.method == "POST":
        print(request.POST) # Debug info
        try:
            title = request.POST.get('title')
            description = request.POST.get('description')
            course_code = request.POST.get('course_code')
            
            if not course_code:
                # Generate from title: e.g. "Intro to Programming" -> "ITP"
                words = title.split()
                if len(words) > 1:
                    course_code = "".join([w[0].upper() for w in words])
                else:
                    course_code = title[:3].upper()
                
                # Make sure it is unique
                base_code = course_code
                counter = 1
                while Course.objects.filter(course_code=course_code).exists():
                    course_code = f"{base_code}{counter}"
                    counter += 1
            
            # 1. Create Course Outline Resource if provided
            outline_file = request.FILES.get('course_outline')
            course_outline_resource = None
            if outline_file:
                course_outline_resource = Resource.objects.create(
                    title=f"{course_code} Outline",
                    type='outline',
                    media=outline_file
                )
            
            # 2. Create the Course
            course = Course.objects.create(
                title=title,
                description=description,
                course_code=course_code,
                course_outline=course_outline_resource,
                created_by=request.user
            )
            
            # 3. Process Exams
            exam_indices = request.POST.getlist('exam_index')
            for idx in exam_indices:
                exam_title = request.POST.get(f'exam_title_{idx}')
                exam_desc = request.POST.get(f'exam_desc_{idx}')
                exam_rules = request.POST.get(f'exam_rules_{idx}')
                exam_marks = request.POST.get(f'exam_marks_{idx}')
                exam_type = request.POST.get(f'exam_type_{idx}')
                instruct_ai = request.POST.get(f'instruct_ai_{idx}')
                exam_date = request.POST.get(f'exam_date_{idx}')
                duration = request.POST.get(f'duration_{idx}')
                
                exam = Exam.objects.create(
                    course=course,
                    title=exam_title,
                    description=exam_desc,
                    rules=exam_rules,
                    marks=exam_marks,
                    exam_type=exam_type,
                    instruct_ai=instruct_ai,
                    exam_date=exam_date if exam_date else None,
                    duration_minutes=int(duration) if duration else 60
                )
                
                # Additional resources (Lecture Notes) for the exam
                resource_indices = request.POST.getlist(f'resource_index_{idx}')
                for r_idx in resource_indices:
                    r_title = request.POST.get(f'resource_title_{idx}_{r_idx}')
                    r_file = request.FILES.get(f'resource_file_{idx}_{r_idx}')
                    
                    if r_file:
                        if not r_title or not r_title.strip():
                            r_title = r_file.name
                        Resource.objects.create(
                            title=r_title,
                            type='lecture',
                            media=r_file,
                            exam=exam
                        )
            
            messages.success(request, f"Course '{course.title}' created successfully!")
            return redirect('teachers:dashboard')
            
        except Exception as e:
            messages.error(request, f"Error creating course: {str(e)}")
            
    return render(request, "teachers/create_course.html")

@login_required
def course_list(request):
    courses = Course.objects.filter(created_by=request.user).order_by('-created_at')
    return render(request, 'teachers/courses.html', {'courses': courses})

@login_required
def course_detail(request, course_id):
    course = get_object_or_404(Course, id=course_id, created_by=request.user)
    student_list = RegisteredCourse.objects.filter(course=course).select_related('student__user').order_by('enrolled_at')
    
    paginator = Paginator(student_list, 10)
    page_number = request.GET.get('page')
    students = paginator.get_page(page_number)
    
    lecture_notes = Resource.objects.filter(exam__course=course, type='lecture').distinct()
    
    return render(request, 'teachers/course_detail.html', {'course': course, 'students': students, 'lecture_notes': lecture_notes})

@login_required
def edit_course(request, course_id):
    course = get_object_or_404(Course, id=course_id, created_by=request.user)
    if request.method == "POST":
        course.title = request.POST.get('title')
        course.description = request.POST.get('description')
        course.course_code = request.POST.get('course_code')
        
        outline_file = request.FILES.get('course_outline')
        if outline_file:
            if course.course_outline:
                course.course_outline.media = outline_file
                course.course_outline.save()
            else:
                res = Resource.objects.create(title=f"{course.course_code} Outline", type='outline', media=outline_file)
                course.course_outline = res
        course.save()
        messages.success(request, "Course details updated successfully.")
        return redirect('teachers:course_detail', course_id=course.id)
        
    return render(request, 'teachers/course_edit.html', {'course': course})

@login_required
def add_exam(request, course_id):
    course = get_object_or_404(Course, id=course_id, created_by=request.user)
    if request.method == "POST":
        exam_title = request.POST.get('exam_title')
        exam_desc = request.POST.get('exam_desc')
        exam_rules = request.POST.get('exam_rules')
        exam_marks = request.POST.get('exam_marks')
        exam_type = request.POST.get('exam_type')
        instruct_ai = request.POST.get('instruct_ai')
        exam_date = request.POST.get('exam_date')
        duration = request.POST.get('duration_minutes')

        exam = Exam.objects.create(
            course=course,
            title=exam_title,
            description=exam_desc,
            rules=exam_rules,
            marks=exam_marks,
            exam_type=exam_type,
            instruct_ai=instruct_ai,
            exam_date=exam_date if exam_date else None,
            duration_minutes=int(duration) if duration else 60
        )
        
        # Add single lecture note if provided
        note_title = request.POST.get('note_title')
        note_file = request.FILES.get('note_file')
        if note_file:
            if not note_title or not note_title.strip():
                note_title = note_file.name
            Resource.objects.create(title=note_title, type='lecture', media=note_file, exam=exam)
            
        messages.success(request, f"Exam '{exam.title}' added successfully!")
        return redirect('teachers:edit_course', course_id=course.id)
    return redirect('teachers:edit_course', course_id=course.id)

@login_required
def exam_list(request):
    exams = Exam.objects.filter(course__created_by=request.user).order_by('-exam_date', '-id')
    return render(request, 'teachers/exams.html', {'exams': exams})

@login_required
def exam_detail(request, exam_id):
    exam = get_object_or_404(Exam, id=exam_id, course__created_by=request.user)
    submissions = AnswerScript.objects.filter(exam=exam).select_related('registered_course__student__user')
    resources = exam.additional_resources.all()
    
    return render(request, 'teachers/exam_detail.html', {'exam': exam, 'submissions': submissions, 'resources': resources})

@login_required
def edit_exam(request, exam_id):
    exam = get_object_or_404(Exam, id=exam_id, course__created_by=request.user)
    
    if request.method == "POST":
        exam.title = request.POST.get('title')
        exam.description = request.POST.get('description')
        exam.rules = request.POST.get('rules')
        
        marks = request.POST.get('marks')
        if marks:
            exam.marks = marks
            
        exam.exam_type = request.POST.get('exam_type')
        exam.status = request.POST.get('status')
        
        exam_date = request.POST.get('exam_date')
        if exam_date:
            exam.exam_date = exam_date
            
        duration = request.POST.get('duration_minutes')
        if duration:
            exam.duration_minutes = duration
            
        exam.instruct_ai = request.POST.get('instruct_ai')
        exam.save()
        
        messages.success(request, "Exam updated successfully.")
        return redirect('teachers:exam_detail', exam_id=exam.id)
        
    return render(request, 'teachers/exam_edit.html', {'exam': exam})

@login_required
def student_detail(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    # Get only the courses this student is taking from THIS active teacher
    registered_courses = RegisteredCourse.objects.filter(student=student, course__created_by=request.user)
    
    submissions = AnswerScript.objects.filter(
        registered_course__student=student, 
        exam__course__created_by=request.user
    )
    
    return render(request, 'teachers/student_detail.html', {
        'student': student, 
        'registered_courses': registered_courses,
        'submissions': submissions
    })

@login_required
def ai_gen_qs(request):
    return render(request, "teachers/ai_gen_questions.html")

@login_required
def evaluate(request):
    return render(request, "teachers/evaluate.html")
