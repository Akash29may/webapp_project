from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User
from students.models import Student
from teachers.models import Teacher

class TeacherSignUpForm(UserCreationForm):
    first_name = forms.CharField(max_length=150, required=True)
    last_name = forms.CharField(max_length=150, required=True)
    email = forms.EmailField(required=True)
    contact_no = forms.CharField(max_length=15, required=False)
    
    # Teacher Profile Fields
    department = forms.CharField(max_length=100, required=True)
    designation = forms.CharField(max_length=100, required=False, help_text="e.g. Senior Lecturer")

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'contact_no')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_teacher = True
        if commit:
            user.save()
            Teacher.objects.create(
                user=user,
                department=self.cleaned_data.get('department'),
                designation=self.cleaned_data.get('designation')
            )
        return user


class StudentSignUpForm(UserCreationForm):
    first_name = forms.CharField(max_length=150, required=True)
    last_name = forms.CharField(max_length=150, required=True)
    email = forms.EmailField(required=True)
    contact_no = forms.CharField(max_length=15, required=False)
    
    # Student Profile Fields
    university = forms.CharField(max_length=255, required=True)
    department = forms.CharField(max_length=100, required=True)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'contact_no')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_student = True
        if commit:
            user.save()
            Student.objects.create(
                user=user,
                university=self.cleaned_data.get('university'),
                department=self.cleaned_data.get('department')
            )
        return user
