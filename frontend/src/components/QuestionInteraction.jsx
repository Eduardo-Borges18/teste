import React, { useState } from 'react';
import axios from 'axios';

const API_BASE = 'http://127.0.0.1:8000/api';

const QuestionInteraction = ({ question }) => {
  const [answer, setAnswer] = useState('');
  const [status, setStatus] = useState('idle'); // 'idle' | 'loading' | 'success' | 'error'
  const [feedback, setFeedback] = useState(null);
  const [errorMsg, setErrorMsg] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!answer.trim()) return;

    setStatus('loading');
    setErrorMsg('');

    try {
      const response = await axios.post(`${API_BASE}/submissions/`, {
        question_id: question.id,
        answer_text: answer,
      });
      setFeedback(response.data);
      setStatus('success');
    } catch (err) {
      console.error(err);
      const serverMsg = err.response?.data?.error;
      setErrorMsg(serverMsg || 'Ocorreu um erro ao processar. Tente novamente.');
      setStatus('error');
    }
  };

  const handleReset = () => {
    setAnswer('');
    setFeedback(null);
    setErrorMsg('');
    setStatus('idle');
  };

  if (!question) {
    return <div className="card"><p>Carregando questão...</p></div>;
  }

  // Determina a cor do badge da nota
  const getScoreClass = (score) => {
    if (score >= 7) return 'score-high';
    if (score >= 4) return 'score-mid';
    return 'score-low';
  };

  return (
    <div className="card">
      <div className="header">
        <h2 className="question-title">{question.title}</h2>
        <p className="question-desc">{question.description}</p>
      </div>

      {status !== 'success' && (
        <form onSubmit={handleSubmit} className="form-group">
          <label htmlFor="answer-input" className="sr-only">Sua resposta</label>
          <textarea
            id="answer-input"
            className="textarea-input"
            placeholder="Desenvolva sua resposta aqui com detalhes..."
            value={answer}
            onChange={(e) => setAnswer(e.target.value)}
            disabled={status === 'loading'}
          />
          <button
            type="submit"
            disabled={status === 'loading' || !answer.trim()}
            className="submit-btn"
          >
            {status === 'loading' ? (
              <>
                <div className="spinner" aria-hidden="true"></div>
                <span>Analisando com IA...</span>
              </>
            ) : 'Enviar Resposta'}
          </button>

          {status === 'error' && (
            <p className="error-text" role="alert">{errorMsg}</p>
          )}
        </form>
      )}

      {/* ---- Renderização do Feedback ---- */}
      {status === 'success' && feedback && (
        <div className="feedback-container">
          {/* Nota em destaque */}
          <div className="score-display">
            <span className={`score-badge ${getScoreClass(feedback.score)}`}>
              {Number(feedback.score).toFixed(1)}
            </span>
            <span className="score-label">/ 10</span>
          </div>

          <h3 className="feedback-title">Análise da Resposta</h3>

          <div className="feedback-box main">
            <h4>💬 Feedback do Professor IA</h4>
            <p>{feedback.constructive_feedback}</p>
          </div>

          <div className="feedback-grid">
            <div className="insight-card strengths">
              <h4><span className="icon">🚀</span> Pontos Fortes</h4>
              <p>{feedback.key_strengths}</p>
            </div>

            <div className="insight-card improvements">
              <h4><span className="icon">🎯</span> Pontos a Melhorar</h4>
              <p>{feedback.areas_for_improvement}</p>
            </div>
          </div>

          <button onClick={handleReset} className="reset-link">
            ↺ Responder novamente
          </button>
        </div>
      )}
    </div>
  );
};

export default QuestionInteraction;
