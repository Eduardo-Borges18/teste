import React, { useState, useEffect } from 'react';
import axios from 'axios';
import QuestionInteraction from './components/QuestionInteraction';
import './index.css';

const API_BASE = 'http://127.0.0.1:8000/api';

function App() {
  const [question, setQuestion] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchQuestion = async () => {
      try {
        const response = await axios.get(`${API_BASE}/questions/`);
        const questions = response.data;
        if (questions && questions.length > 0) {
          setQuestion(questions[0]);
        } else {
          setError('Nenhuma questão encontrada no sistema.');
        }
      } catch (err) {
        console.error('Erro ao carregar questão:', err);
        setError(
          'Não foi possível conectar ao servidor. Certifique-se que o backend está rodando em http://127.0.0.1:8000.'
        );
      } finally {
        setLoading(false);
      }
    };

    fetchQuestion();
  }, []);

  return (
    <div className="app-container">
      <header className="app-header">
        <h1 className="app-logo">EduAI Tutor</h1>
        <p className="app-subtitle">
          Plataforma de aprendizado com feedback inteligente powered by Gemini
        </p>
      </header>

      <main>
        {loading && (
          <div className="card" style={{ textAlign: 'center' }}>
            <div className="spinner" style={{ margin: '0 auto', borderTopColor: 'var(--primary)' }}></div>
            <p style={{ marginTop: '1rem', color: 'var(--text-muted)' }}>Carregando atividade...</p>
          </div>
        )}

        {error && (
          <div className="card error-card">
            <p className="error-text" style={{ fontSize: '1rem', marginTop: 0 }}>{error}</p>
          </div>
        )}

        {!loading && !error && question && (
          <QuestionInteraction question={question} />
        )}
      </main>

      <footer className="app-footer">
        <p>EduAI Tutor MVP &copy; {new Date().getFullYear()} — Feedback gerado por Google Gemini</p>
      </footer>
    </div>
  );
}

export default App;
