from rest_framework import serializers
from .models import Question, Submission, Feedback


class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ['id', 'title', 'description', 'created_at']
        # 'rubric' é intencionalmente omitida — é informação interna do professor.


class FeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields = [
            'id',
            'submission',
            'score',
            'constructive_feedback',
            'key_strengths',
            'areas_for_improvement',
            'generated_at',
        ]


class SubmissionSerializer(serializers.ModelSerializer):
    feedback = FeedbackSerializer(read_only=True)

    class Meta:
        model = Submission
        fields = ['id', 'question', 'answer_text', 'submitted_at', 'feedback']
