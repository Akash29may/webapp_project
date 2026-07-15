from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.conf import settings

# 1. Student Profile
class Student(models.Model):
    # Use settings.AUTH_USER_MODEL to refer to your custom User in the 'core' app
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='student_profile'
    )
    university = models.CharField(max_length=255)
    department = models.CharField(max_length=100)

    def __str__(self):
        return f"Student: {self.user.username}"

# 2. Registered Course (Enrollment Table)
class RegisteredCourse(models.Model):
    student = models.ForeignKey(
        Student, 
        on_delete=models.CASCADE, 
        related_name='enrolled_courses'
    )
    # Using string reference to 'teachers.Course' to break circular import
    course = models.ForeignKey(
        'teachers.Course', 
        on_delete=models.CASCADE, 
        related_name='enrolled_students'
    )

    enrolled_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'course') # Prevents double enrollment

    def __str__(self):
        return f"{self.student.user.username} -> {self.course.title}"

# 3. Answer Script (Exam Submissions)
class AnswerScript(models.Model):
    registered_course = models.ForeignKey(
        RegisteredCourse, 
        on_delete=models.CASCADE, 
        related_name='submissions'
    )
    # Using string reference to 'teachers.Exam'
    exam = models.ForeignKey(
        'teachers.Exam', 
        on_delete=models.CASCADE, 
        related_name='submitted_scripts'
    )
    
    # Using string reference to 'teachers.Resource'
    # Stores the actual file/JSON of student answers
    answer_resource = models.OneToOneField(
        'teachers.Resource', 
        on_delete=models.CASCADE, 
        related_name='student_answer'
    )
    
    marks = models.FloatField(default=0.0)
    ai_review = models.TextField(blank=True, null=True, help_text="Raw feedback from AI evaluation")
    is_evaluated = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.registered_course.student.user.username} - {self.exam.title}"

# 4. Review (Student Feedback on Course)
class Review(models.Model):
    RATING_CHOICES = (
        (1, 'Very Unsatisfied'),
        (2, 'Unsatisfied'),
        (3, 'Moderate'),
        (4, 'Satisfied'),
        (5, 'Very Satisfied'),
    )
    registered_course = models.OneToOneField(
        RegisteredCourse, 
        on_delete=models.CASCADE, 
        related_name='course_review'
    )
    rating = models.PositiveSmallIntegerField(
        choices=RATING_CHOICES, 
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    message = models.TextField()

    def __str__(self):
        return f"Review for {self.registered_course.course.title}"