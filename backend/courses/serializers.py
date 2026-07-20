from rest_framework import serializers

from .models import Course, Module, Resource


class ResourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resource
        fields = ("id", "module", "title", "file", "text_body", "order")
        read_only_fields = ("module",)


class ModuleSerializer(serializers.ModelSerializer):
    resources = ResourceSerializer(many=True, read_only=True)

    class Meta:
        model = Module
        fields = ("id", "course", "title", "order", "resources")
        read_only_fields = ("course",)


class CourseSerializer(serializers.ModelSerializer):
    modules = ModuleSerializer(many=True, read_only=True)

    class Meta:
        model = Course
        fields = ("id", "title", "description", "created_at", "modules")
        read_only_fields = ("created_at",)
