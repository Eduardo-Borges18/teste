from django.urls import path
from .views import QuestionListView, QuestionDetailView, SubmitAnswerView

urlpatterns = [
    path('questions/', QuestionListView.as_view(), name='question-list'),
    path('questions/<int:pk>/', QuestionDetailView.as_view(), name='question-detail'),
    path('submissions/', SubmitAnswerView.as_view(), name='submit-answer'),
]
