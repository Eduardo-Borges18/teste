from django.contrib import admin
from .models import Question, Submission, Feedback


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at')
    search_fields = ('title', 'description')


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ('id', 'question', 'user', 'submitted_at')
    list_filter = ('submitted_at', 'question')
    readonly_fields = ('submitted_at',)


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('id', 'submission', 'score', 'generated_at')
    list_filter = ('generated_at',)
    readonly_fields = ('generated_at',)
