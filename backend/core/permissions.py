from rest_framework.permissions import BasePermission


class IsTeacher(BasePermission):
    message = "Teacher account required."

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_teacher)


class IsStudent(BasePermission):
    message = "Student account required."

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_student)
