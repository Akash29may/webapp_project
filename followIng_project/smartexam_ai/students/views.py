from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Student, RegisteredCourse, AnswerScript
from teachers.models import Exam, Course
from .services.student_rank import calculate_student_rank_in_course

@login_required
def dashboard(request):
    try:
        student = request.user.student_profile
    except Student.DoesNotExist:
        # Handle case where user is not a student
        return render(request, "students/dashboard.html", {"error": "Student profile not found."})

    enrolled_courses = RegisteredCourse.objects.filter(student=student).select_related('course')
    active_courses_count = enrolled_courses.count()
    
    # Exams taken
    scripts = AnswerScript.objects.filter(registered_course__student=student)
    total_exams_taken = scripts.count()
    
    # Calculate simple avg score
    total_marks = sum(script.marks for script in scripts if script.marks is not None)
    avg_score = total_marks / total_exams_taken if total_exams_taken > 0 else 0
    
    # Courses list for the UI
    courses_data = []
    for rc in enrolled_courses:
        # Utilize the new complex ranking logic service
        courses_data.append({
            'id': rc.course.id,
            'title': rc.course.title,
            'teacher': rc.course.created_by.get_full_name() or rc.course.created_by.username,
            'rank': calculate_student_rank_in_course(student, rc.course)
        })
        
    # Requires Attention: Active exams student hasn't submitted yet
    enrolled_course_ids = enrolled_courses.values_list('course_id', flat=True)
    active_exams = Exam.objects.filter(course_id__in=enrolled_course_ids, status='active')
    
    submitted_exam_ids = scripts.values_list('exam_id', flat=True)
    pending_exams = active_exams.exclude(id__in=submitted_exam_ids)
    
    # Recent evaluations (last 3)
    recent_evaluations = scripts.filter(is_evaluated=True).order_by('-id')[:3]

    context = {
        'student': student,
        'active_courses_count': active_courses_count,
        'total_exams_taken': total_exams_taken,
        'avg_score': round(avg_score, 1),
        'courses_data': courses_data,
        'pending_exams': pending_exams,
        'recent_evaluations': recent_evaluations,
    }
    
    return render(request, "students/dashboard.html", context)

@login_required
def browse_courses(request):
    try:
        student = request.user.student_profile
    except Student.DoesNotExist:
        return redirect('dashboard')
        
    enrolled_course_ids = RegisteredCourse.objects.filter(student=student).values_list('course_id', flat=True)
    # Get all courses, annotate if the student is enrolled
    all_courses = Course.objects.all().order_by('-created_at')
    
    context = {
        'student': student,
        'courses': all_courses,
        'enrolled_course_ids': enrolled_course_ids,
    }
    return render(request, "students/browse_courses.html", context)

@login_required
def course_detail(request, course_id):
    try:
        student = request.user.student_profile
    except Student.DoesNotExist:
        return redirect('dashboard')
        
    course = get_object_or_404(Course, id=course_id)
    is_enrolled = RegisteredCourse.objects.filter(student=student, course=course).exists()
    
    total_enrolled = RegisteredCourse.objects.filter(course=course).count()
    
    rank = None
    exams_data = []
    if is_enrolled:
        try:
            rc = RegisteredCourse.objects.get(student=student, course=course)
            subs = dict(AnswerScript.objects.filter(registered_course=rc).values_list('exam_id', 'id'))
            for ex in course.exams.all():
                exams_data.append({'id': ex.id, 'title': ex.title, 'status': ex.status, 'marks': ex.marks, 'duration': ex.duration_minutes, 'is_submitted': ex.id in subs})
        except:
            pass
    else:
        for ex in course.exams.all():
            exams_data.append({'id': ex.id, 'title': ex.title, 'status': ex.status, 'marks': ex.marks, 'duration': ex.duration_minutes, 'is_submitted': False})
            
    if is_enrolled:
        # Utilize the new complex ranking logic service
        rank = calculate_student_rank_in_course(student, course)
        
    context = {
        'student': student,
        'course': course,
        'is_enrolled': is_enrolled,
        'total_enrolled': total_enrolled,
        'rank': rank,
        'exams': exams_data,
        'lecture_notes': [r for ex in course.exams.all() for r in ex.additional_resources.filter(type='lecture')] if is_enrolled else [],
    }
    return render(request, "students/course_detail.html", context)


@login_required
def enroll_course(request, course_id):
    if request.method == 'POST':
        try:
            student = request.user.student_profile
        except Student.DoesNotExist:
            messages.error(request, "Only students can enroll in courses.")
            return redirect('dashboard')
            
        course = get_object_or_404(Course, id=course_id)
        
        # Check if already enrolled
        if RegisteredCourse.objects.filter(student=student, course=course).exists():
            messages.info(request, "You are already enrolled in this course.")
        else:
            RegisteredCourse.objects.create(student=student, course=course)
            messages.success(request, f"Successfully enrolled in {course.title}!")
            
    return redirect('students:course_detail', course_id=course_id)

@login_required
def exam_detail(request, exam_id):
    try:
        student = request.user.student_profile
    except Student.DoesNotExist:
        return redirect('dashboard')
        
    exam = get_object_or_404(Exam, id=exam_id)
    course = exam.course
    is_enrolled = RegisteredCourse.objects.filter(student=student, course=course).exists()
    
    if not is_enrolled:
        messages.error(request, "You must be enrolled in the course to view its exams.")
        return redirect('students:course_detail', course_id=course.id)
        
    # Check if student already submitted this exam
    rc = RegisteredCourse.objects.get(student=student, course=course)
    submission = AnswerScript.objects.filter(registered_course=rc, exam=exam).first()
    
    context = {
        'student': student,
        'exam': exam,
        'course': course,
        'submission': submission,
        'lecture_notes': exam.additional_resources.filter(type='lecture'),
    }
    return render(request, "students/exam_detail.html", context)


@login_required
def exams_list(request):
    try:
        student = request.user.student_profile
    except Student.DoesNotExist:
        return redirect('dashboard')
        
    enrolled_courses = RegisteredCourse.objects.filter(student=student)
    enrolled_course_ids = enrolled_courses.values_list('course_id', flat=True)
    
    # Get all exams for enrolled courses
    exams = Exam.objects.filter(course_id__in=enrolled_course_ids).order_by('exam_date', '-id')
    
    # Get all submissions to know which are completed
    submissions = AnswerScript.objects.filter(registered_course__student=student)
    submitted_exam_ids = set(submissions.values_list('exam_id', flat=True))
    
    # Annotate exams with submission status for the template
    exams_data = []
    for exam in exams:
        is_submitted = exam.id in submitted_exam_ids
        exams_data.append({
            'exam': exam,
            'is_submitted': is_submitted,
            'course_title': exam.course.title,
            'course_code': exam.course.course_code
        })
        
    context = {
        'student': student,
        'exams_data': exams_data,
    }
    return render(request, "students/browse_exams.html", context)


@login_required
def take_exam(request, exam_id):
    try:
        student = request.user.student_profile
    except Student.DoesNotExist:
        return redirect('dashboard')
        
    exam = get_object_or_404(Exam, id=exam_id)
    course = exam.course
    
    # Validation gates
    if not RegisteredCourse.objects.filter(student=student, course=course).exists():
        messages.error(request, "You are not enrolled in this course.")
        return redirect('students:dashboard')
        
    if exam.status != 'active':
        messages.warning(request, "This exam is not active yet or has been closed.")
        return redirect('students:exam_detail', exam_id=exam.id)
        
    rc = RegisteredCourse.objects.get(student=student, course=course)
    
    if AnswerScript.objects.filter(registered_course=rc, exam=exam).exists():
        messages.info(request, "You have already submitted this exam.")
        return redirect('students:exam_detail', exam_id=exam.id)
        
    if request.method == 'POST':
        # Collect answers dynamically
        answers = {}
        for key, value in request.POST.items():
            if key.startswith('q_'):
                answers[key] = value
                
        # Tab switch and cheat data
        cheat_flags = {
            'tab_switches': request.POST.get('tab_switches', 0),
            'was_fullscreen_broken': request.POST.get('fullscreen_broken', False)
        }
                
        # Calculate objective score if possible (simple matching for MCQ if answer key exists)
        # Note: True evaluation usually happens asynchronously via AI, so here we mostly just save.
        
        # Create Resource for answers according to schema
        from teachers.models import Resource
        answer_res = Resource.objects.create(
            title=f"Answers for {exam.title}",
            type='answer',
            script={"answers": answers, "cheat_flags": cheat_flags},
            exam=exam
        )
        
        AnswerScript.objects.create(
            registered_course=rc,
            exam=exam,
            answer_resource=answer_res,
            ai_review=f"Activity Monitor - Tab Switches: {cheat_flags['tab_switches']}, Fullscreen Broken: {cheat_flags['was_fullscreen_broken']}",
            is_evaluated=False
        )
        
        messages.success(request, "Exam submitted successfully!")
        return redirect('students:exam_detail', exam_id=exam.id)
        
    # GET method - render exam environment
    # Note: production systems would check/generate a unique exam session ticket here
    question_data = []
    if exam.question_script and exam.question_script.script:
        question_data = exam.question_script.script
        
    context = {
        'exam': exam,
        'course': course,
        'questions': question_data,
        # Default mock questions if none provided (for UI testing)
        'mock': not bool(question_data) 
    }
    
    return render(request, "students/live_exam.html", context)


@login_required
def answer_script(request, exam_id):
    try:
        student = request.user.student_profile
    except Student.DoesNotExist:
        return redirect('dashboard')
        
    exam = get_object_or_404(Exam, id=exam_id)
    course = exam.course
    
    rc = get_object_or_404(RegisteredCourse, student=student, course=course)
    submission = get_object_or_404(AnswerScript, registered_course=rc, exam=exam)
    
    # Parse questions from the exam question script
    questions_data = []
    if exam.question_script and exam.question_script.script:
        questions_data = exam.question_script.script
        
    # Student's answers stored inside answer_resource script
    student_answers = {}
    if submission.answer_resource and submission.answer_resource.script:
        student_answers = submission.answer_resource.script.get('answers', {})
        
    # Zipping questions with student answers
    qa_list = []
    for q in questions_data:
        q_id = str(q.get('id', ''))
        answer = student_answers.get(f'q_{q_id}', 'Not Answered')
        qa_list.append({
            'question': q,
            'answer': answer
        })
        
    context = {
        'exam': exam,
        'course': course,
        'submission': submission,
        'qa_list': qa_list
    }
    return render(request, "students/answer_script.html", context)



