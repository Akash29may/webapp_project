from django.db.models import Sum
from django.db.models.functions import Coalesce
from students.models import RegisteredCourse

def calculate_student_rank_in_course(student, course):
    """
    Calculates the given student's rank within a specific course based on 
    the total marks obtained across all evaluated exams in that course.
    """
    # If the student hasn't submitted any exams yet, they technically have no applicable rank.
    target_enrollment = RegisteredCourse.objects.filter(student=student, course=course).first()
    if not target_enrollment or not target_enrollment.submissions.exists():
        return "N/A"

    # Annotate all enrolled students with their total sum of marks in this course.
    # Coalesce handles cases where a student has 0 submissions, defaulting to 0.0
    ranked_enrollments = RegisteredCourse.objects.filter(course=course).annotate(
        total_marks=Coalesce(Sum('submissions__marks'), 0.0)
    ).order_by('-total_marks', 'enrolled_at')
    
    # Iterate to find the student's rank
    current_rank = 1
    previous_marks = None
    actual_placement = 1
    
    for enrollment in ranked_enrollments:
        # Handle tie-breaking logic (students with same marks get same rank)
        if previous_marks is None:
            previous_marks = enrollment.total_marks
            
        if enrollment.total_marks < previous_marks:
            current_rank = actual_placement
            previous_marks = enrollment.total_marks
            
        if enrollment.student == student:
            # Suffix styling (1st, 2nd, 3rd, etc.)
            suffix = 'th'
            if 11 <= (current_rank % 100) <= 13:
                suffix = 'th'
            elif current_rank % 10 == 1:
                suffix = 'st'
            elif current_rank % 10 == 2:
                suffix = 'nd'
            elif current_rank % 10 == 3:
                suffix = 'rd'
                
            return f"{current_rank}{suffix}"
            
        actual_placement += 1
        
    return "N/A"
