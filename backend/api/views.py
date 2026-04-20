import json
import logging
import os

from google import genai
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response

from .models import Question, Submission, Feedback
from .serializers import QuestionSerializer, FeedbackSerializer

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# System Prompt – diretrizes pedagógicas enviadas ao Gemini
# ---------------------------------------------------------------------------
SYSTEM_PROMPT = (
    "Você é um experiente professor tutor de alunos universitários.\n"
    "Sua tarefa é analisar a resposta de um aluno com base no enunciado e "
    "na rubrica de correção fornecidos.\n\n"
    "Diretrizes:\n"
    "- Nunca entregue a resposta pronta; ajude o aluno a raciocinar.\n"
    "- Seja encorajador e construtivo; destaque o que ele já compreendeu.\n"
    "- Aponte erros conceituais ou inconsistências de forma gentil.\n\n"
    "Responda ESTRITAMENTE em formato JSON válido (sem markdown, sem ```), "
    "com as seguintes chaves:\n"
    '  "score": número float de 0 a 10 (até 2 casas decimais),\n'
    '  "key_strengths": string com os pontos fortes e acertos do aluno,\n'
    '  "areas_for_improvement": string com o que faltou ou estava superficial,\n'
    '  "constructive_feedback": string com feedback pedagógico encorajador.\n'
)


class QuestionListView(generics.ListAPIView):
    """GET /api/questions/ — lista todas as questões disponíveis."""
    queryset = Question.objects.all().order_by('-created_at')
    serializer_class = QuestionSerializer


class QuestionDetailView(generics.RetrieveAPIView):
    """GET /api/questions/<id>/ — detalhes de uma questão."""
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer


class SubmitAnswerView(APIView):
    """POST /api/submissions/ — recebe resposta do aluno, envia ao Gemini e
    persiste o feedback gerado."""

    def post(self, request):
        question_id = request.data.get('question_id')
        answer_text = request.data.get('answer_text', '').strip()

        # ---------- Validação de entrada ----------
        if not question_id or not answer_text:
            return Response(
                {"error": "Os campos 'question_id' e 'answer_text' são obrigatórios."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            question = Question.objects.get(id=question_id)
        except Question.DoesNotExist:
            return Response(
                {"error": "Questão não encontrada."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # ---------- 1) Persistir a submissão ----------
        submission = Submission.objects.create(
            question=question,
            answer_text=answer_text,
        )

        # ---------- 2) Montar prompt e chamar a API do Gemini ----------
        user_prompt = (
            f"Enunciado: {question.description}\n"
            f"Rubrica de Correção: {question.rubric}\n"
            f"Resposta submetida pelo Aluno: {answer_text}\n\n"
            "Realize a correção e retorne APENAS o JSON, sem nenhum outro texto."
        )

        api_key = os.environ.get("GEMINI_API_KEY", "").strip()
        if not api_key:
            logger.error("GEMINI_API_KEY não está configurada nas variáveis de ambiente.")
            return Response(
                {"error": "Chave da API de IA não configurada no servidor."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        try:
            client = genai.Client(api_key=api_key)

            # Combina o system prompt com o user prompt em uma única mensagem
            full_prompt = SYSTEM_PROMPT + "\n---\n" + user_prompt

            response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=full_prompt,
                config=genai.types.GenerateContentConfig(
                    temperature=0.4,
                    max_output_tokens=1024,
                ),
            )

            raw_text = response.text

            # Sanitizar possíveis marcadores markdown na resposta
            if "```json" in raw_text:
                raw_text = raw_text.split("```json")[1].split("```")[0].strip()
            elif "```" in raw_text:
                raw_text = raw_text.split("```")[1].split("```")[0].strip()

            ai_data = json.loads(raw_text)

        except json.JSONDecodeError as e:
            logger.exception("Resposta do Gemini não é JSON válido: %s", e)
            return Response(
                {"error": "A resposta da IA não pôde ser processada. Tente novamente."},
                status=status.HTTP_502_BAD_GATEWAY,
            )
        except Exception as e:
            logger.exception("Erro inesperado na integração com o Gemini: %s", e)
            return Response(
                {"error": "Serviço de IA temporariamente indisponível."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        # ---------- 3) Salvar feedback no banco ----------
        feedback = Feedback.objects.create(
            submission=submission,
            score=ai_data.get('score', 0.0),
            key_strengths=ai_data.get('key_strengths', ''),
            areas_for_improvement=ai_data.get('areas_for_improvement', ''),
            constructive_feedback=ai_data.get('constructive_feedback', ''),
        )

        return Response(FeedbackSerializer(feedback).data, status=status.HTTP_201_CREATED)
