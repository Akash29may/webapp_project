from django.urls import path

from .views import (
    AttemptResultView,
    AttemptStateView,
    ExamResultsView,
    ExamViewSet,
    GenerateQuestionsView,
    PublishedExamListView,
    QuestionViewSet,
    SaveAnswerView,
    StartAttemptView,
    SubmitAttemptView,
    WarnView,
)

exam_list = ExamViewSet.as_view({"get": "list", "post": "create"})
exam_detail = ExamViewSet.as_view(
    {"get": "retrieve", "patch": "partial_update", "delete": "destroy"}
)
question_create = QuestionViewSet.as_view({"post": "create"})
question_detail = QuestionViewSet.as_view({"patch": "partial_update", "delete": "destroy"})

urlpatterns = [
    # teacher authoring
    path("exams/", exam_list, name="exam-list"),
    path("exams/<int:pk>/", exam_detail, name="exam-detail"),
    path("exams/<int:exam_pk>/questions/", question_create, name="question-create"),
    path("questions/<int:pk>/", question_detail, name="question-detail"),
    path("exams/<int:exam_pk>/generate/", GenerateQuestionsView.as_view(), name="exam-generate"),
    path("exams/<int:exam_pk>/results/", ExamResultsView.as_view(), name="exam-results"),
    # student engine
    path("student/exams/", PublishedExamListView.as_view(), name="published-exams"),
    path("exams/<int:exam_pk>/attempt/", StartAttemptView.as_view(), name="start-attempt"),
    path("attempts/<int:pk>/", AttemptStateView.as_view(), name="attempt-state"),
    path("attempts/<int:pk>/answer/", SaveAnswerView.as_view(), name="save-answer"),
    path("attempts/<int:pk>/submit/", SubmitAttemptView.as_view(), name="submit-attempt"),
    path("attempts/<int:pk>/warn/", WarnView.as_view(), name="warn"),
    path("attempts/<int:pk>/result/", AttemptResultView.as_view(), name="attempt-result"),
]
