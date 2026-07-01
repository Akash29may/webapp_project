from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib import messages
from core.forms import StudentSignUpForm, TeacherSignUpForm

# Create your views here.

def landpage(request) :
    return render(request, "index.html")

def login(request) :
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user_type = request.POST.get("user_type")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            auth_login(request, user)
            if user.is_teacher and user_type == "teacher":
                return redirect("teachers:dashboard")
            elif user.is_student and user_type == "student":
                try:
                    return redirect("students:dashboard")
                except:
                    return redirect("landpage")
            else:
                messages.error(request, f"You are not registered as a {user_type}.")
                return render(request, "login.html")
        else:
            messages.error(request, "Invalid username or password.")
            return render(request, "login.html")
            
    return render(request, "login.html")

def base(request) :
    return render(request, "base.html")

def register(request):
    student_form = StudentSignUpForm()
    teacher_form = TeacherSignUpForm()

    if request.method == "POST":
        user_type = request.POST.get("user_type")
        if user_type == "student":
            student_form = StudentSignUpForm(request.POST)
            if student_form.is_valid():
                user = student_form.save()
                auth_login(request, user)
                messages.success(request, 'Student account created successfully!')
                return redirect('students:dashboard')
            else:
                messages.error(request, 'Please correct the errors in the Student registration form.')
        elif user_type == "teacher":
            teacher_form = TeacherSignUpForm(request.POST)
            if teacher_form.is_valid():
                user = teacher_form.save()
                auth_login(request, user)
                messages.success(request, 'Teacher account created successfully!')
                return redirect('teachers:dashboard')
            else:
                messages.error(request, 'Please correct the errors in the Teacher registration form.')

    return render(request, "register.html", {
        'student_form': student_form, 
        'teacher_form': teacher_form
    })

def logout(request) :
    auth_logout(request)
    return redirect("landpage")