from django.urls import path

from .views import CourseViewSet, ModuleViewSet, ResourceViewSet

course_list = CourseViewSet.as_view({"get": "list", "post": "create"})
course_detail = CourseViewSet.as_view(
    {"get": "retrieve", "patch": "partial_update", "delete": "destroy"}
)
module_create = ModuleViewSet.as_view({"post": "create"})
module_detail = ModuleViewSet.as_view(
    {"get": "retrieve", "patch": "partial_update", "delete": "destroy"}
)
resource_create = ResourceViewSet.as_view({"post": "create"})
resource_detail = ResourceViewSet.as_view(
    {"get": "retrieve", "patch": "partial_update", "delete": "destroy"}
)

urlpatterns = [
    path("courses/", course_list, name="course-list"),
    path("courses/<int:pk>/", course_detail, name="course-detail"),
    path("courses/<int:course_pk>/modules/", module_create, name="module-create"),
    path("modules/<int:pk>/", module_detail, name="module-detail"),
    path("modules/<int:module_pk>/resources/", resource_create, name="resource-create"),
    path("resources/<int:pk>/", resource_detail, name="resource-detail"),
]
