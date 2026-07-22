from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.exceptions import PermissionDenied

from core.permissions import IsTeacher

from .models import Course, Module, Resource
from .serializers import CourseSerializer, ModuleSerializer, ResourceSerializer


class CourseViewSet(viewsets.ModelViewSet):
    serializer_class = CourseSerializer
    permission_classes = [IsTeacher]

    def get_queryset(self):
        return Course.objects.filter(teacher=self.request.user.teacher)

    def perform_create(self, serializer):
        serializer.save(teacher=self.request.user.teacher)


class ModuleViewSet(viewsets.ModelViewSet):
    serializer_class = ModuleSerializer
    permission_classes = [IsTeacher]

    def get_queryset(self):
        return Module.objects.filter(course__teacher=self.request.user.teacher)

    def perform_create(self, serializer):
        course = get_object_or_404(
            Course, pk=self.kwargs["course_pk"], teacher=self.request.user.teacher
        )
        serializer.save(course=course)


class ResourceViewSet(viewsets.ModelViewSet):
    serializer_class = ResourceSerializer
    permission_classes = [IsTeacher]

    def get_queryset(self):
        return Resource.objects.filter(module__course__teacher=self.request.user.teacher)

    def perform_create(self, serializer):
        module = get_object_or_404(
            Module,
            pk=self.kwargs["module_pk"],
            course__teacher=self.request.user.teacher,
        )
        serializer.save(module=module)
