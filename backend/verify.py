import django
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from api.views import SubmitAnswerView, QuestionListView, QuestionDetailView
from api.models import Question, Submission, Feedback
from api.serializers import QuestionSerializer, FeedbackSerializer, SubmissionSerializer

print("OK - Todos os imports verificados com sucesso")
print(f"Questões no BD: {Question.objects.count()}")
