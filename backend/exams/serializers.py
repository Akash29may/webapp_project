from django.db import transaction
from rest_framework import serializers

from .models import Answer, Choice, Exam, ExamAttempt, Question


# ---- Teacher authoring serializers ----------------------------------------
class ChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Choice
        fields = ("id", "text", "is_correct")


class QuestionSerializer(serializers.ModelSerializer):
    choices = ChoiceSerializer(many=True, required=False)

    class Meta:
        model = Question
        fields = ("id", "qtype", "text", "marks", "difficulty", "model_answer", "order", "choices")

    def validate(self, attrs):
        qtype = attrs.get("qtype", getattr(self.instance, "qtype", Question.MCQ))
        choices = attrs.get("choices")
        if qtype == Question.MCQ:
            if choices is None and self.instance is None:
                raise serializers.ValidationError({"choices": "MCQ needs exactly 4 choices."})
            if choices is not None:
                if len(choices) != 4:
                    raise serializers.ValidationError({"choices": "MCQ needs exactly 4 choices."})
                correct = [c for c in choices if c.get("is_correct")]
                if len(correct) != 1:
                    raise serializers.ValidationError(
                        {"choices": "MCQ needs exactly one correct choice."}
                    )
        elif qtype == Question.SUBJECTIVE:
            if not attrs.get("model_answer") and self.instance is None:
                raise serializers.ValidationError(
                    {"model_answer": "Subjective questions require a model answer."}
                )
        return attrs

    @transaction.atomic
    def create(self, validated_data):
        choices = validated_data.pop("choices", [])
        question = Question.objects.create(**validated_data)
        for choice in choices:
            Choice.objects.create(question=question, **choice)
        return question

    @transaction.atomic
    def update(self, instance, validated_data):
        choices = validated_data.pop("choices", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if choices is not None:
            instance.choices.all().delete()
            for choice in choices:
                Choice.objects.create(question=instance, **choice)
        return instance


class ExamSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=True)
    total_marks = serializers.IntegerField(read_only=True)

    class Meta:
        model = Exam
        fields = (
            "id", "course", "title", "duration_min", "is_published",
            "created_at", "total_marks", "questions",
        )
        read_only_fields = ("created_at",)


# ---- Student "take" serializers (NEVER expose is_correct / model_answer) ---
class ChoiceTakeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Choice
        fields = ("id", "text")


class QuestionTakeSerializer(serializers.ModelSerializer):
    choices = ChoiceTakeSerializer(many=True, read_only=True)

    class Meta:
        model = Question
        fields = ("id", "qtype", "text", "marks", "order", "choices")


# ---- Student-facing published exam list ------------------------------------
class PublishedExamSerializer(serializers.ModelSerializer):
    teacher_name = serializers.SerializerMethodField()
    question_count = serializers.SerializerMethodField()
    total_marks = serializers.IntegerField(read_only=True)

    class Meta:
        model = Exam
        fields = ("id", "title", "duration_min", "teacher_name", "question_count", "total_marks")

    def get_teacher_name(self, obj):
        return obj.teacher.user.get_full_name() or obj.teacher.user.username

    def get_question_count(self, obj):
        return obj.questions.count()
