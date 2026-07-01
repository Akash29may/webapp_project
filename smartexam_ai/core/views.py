from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib import messages
from .forms import StudentSignUpForm, TeacherSignUpForm

def register_student(request):
    if request.method == 'POST':
        form = StudentSignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful! Welcome to SmartExam AI.')
            return redirect('home')  # Assume we have a 'home' URL name
    else:
        form = StudentSignUpForm()
    return render(request, 'core/register_student.html', {'form': form})

def register_teacher(request):
    if request.method == 'POST':
        form = TeacherSignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful! Welcome to SmartExam AI.')
            return redirect('home')  # Assume we have a 'home' URL name
    else:
        form = TeacherSignUpForm()
    return render(request, 'core/register_teacher.html', {'form': form})
