from django.db import models
from django.conf import settings

# 1. Teacher Model
class Teacher(models.Model):
    # Use settings.AUTH_USER_MODEL for best practice with custom Users
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='teacher_profile'
    )
    
    department = models.CharField(max_length=100, blank=True)
    # Note: 'placeholder' is not a valid Django model field argument, 
    # use help_text for admin-side guidance.
    designation = models.CharField(max_length=100, help_text="e.g. Senior Lecturer", blank=True)

    def __str__(self):
        return f"Prof. {self.user.username}"

# 2. Resource Model 
class Resource(models.Model):
    RESOURCE_TYPES = (
        ('question', 'Question Script'),
        ('answer', 'Answer Key'),
        ('outline', 'Course Outline'),
        ('lecture', 'Lecture Material'),
    )
    title = models.CharField(max_length=255)
    type = models.CharField(max_length=20, choices=RESOURCE_TYPES)
    media = models.FileField(upload_to='resources/', null=True, blank=True)
    script = models.JSONField(null=True, blank=True)

    # String reference to 'Exam' handles the fact that Exam is defined below
    exam = models.ForeignKey(
        'Exam', 
        on_delete=models.CASCADE, 
        related_name='additional_resources', 
        null=True, 
        blank=True
    )
    
    def __str__(self):
        return f"{self.title} ({self.type})"

# 3. Course Model
class Course(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    course_code = models.CharField(max_length=20, unique=True)
    course_outline = models.OneToOneField(
        Resource, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='course_outline'
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='courses'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def total_exams(self):
        return self.exams.count()

    def __str__(self):
        return self.title

# 4. Exam Model
class Exam(models.Model):
    EXAM_TYPES = (
        ('mcq', 'MCQ'),
        ('subjective', 'Subjective'),
        ('both', 'Both'),
    )
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('active', 'Active'),
        ('completed', 'Completed'),
    )
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='exams')
    title = models.CharField(max_length=255)
    description = models.TextField()
    rules = models.TextField()
    marks = models.PositiveIntegerField(default=100)
    exam_type = models.CharField(max_length=15, choices=EXAM_TYPES)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='pending')
    exam_date = models.DateTimeField(null=True, blank=True)
    duration_minutes = models.PositiveIntegerField(default=60, help_text="Duration in minutes")
    
    question_script = models.OneToOneField(
        Resource, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='exam_qs_script'
    )

    instruct_ai = models.TextField(help_text="Custom instructions for AI evaluation/proctoring")
    ai_generation_done = models.BooleanField(default=False, help_text="Indicates if AI has completed generating the QS and Answer Key")

    def __str__(self):
        return self.title
    
# 5. Suggestion (Performance Feedback)
class Suggestion(models.Model):
    # IMPORTANT: Reference 'students.RegisteredCourse' as a string 
    # to prevent Circular Import errors.
    registered_course = models.OneToOneField(
        'students.RegisteredCourse', 
        on_delete=models.CASCADE, 
        related_name='ai_suggestions'
    )
    review_summary = models.TextField(help_text="Summary of student performance")
    suggestion_text = models.TextField(help_text="AI recommended study path")
    is_ai_suggestion = models.BooleanField(default=True)

    def __str__(self):
        # Access user through the string-referenced model's relationship
        return f"Suggestion for {self.registered_course.student.user.username}"