from django.contrib import admin

from .models import Course, Module, Resource

admin.site.register(Course)
admin.site.register(Module)
admin.site.register(Resource)
