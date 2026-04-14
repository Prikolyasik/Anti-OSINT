import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { FaChartLine, FaShieldAlt, FaExclamationTriangle, FaCheck, FaEnvelope, FaUserSecret, FaKey } from 'react-icons/fa';
import { RadarChart, PolarGrid, PolarAngleAxis, Radar, ResponsiveContainer, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Cell } from 'recharts';
import axios from 'axios';
import API_URL from '../config';
import './PrivacyScore.css';

const PrivacyScore = () => {
  const [email, setEmail] = useState('');
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const calculateScore = async (e) => {
    e.preventDefault();
    if (!email && !username && !password) return;
    
    setLoading(true);
    setError(null);
    
    try {
      const response = await axios.post(`${API_URL}/privacy/score`, {
        email: email || undefined,
        username: username || undefined,
        password: password || undefined
      });
      setResult(response.data);
    } catch (err) {
      setError('Ошибка при расчёте рейтинга приватности.');
    } finally {
      setLoading(false);
    }
  };

  const getScoreColor = (score) => {
    if (score >= 80) return '#00ff88';
    if (score >= 60) return '#00f0ff';
    if (score >= 40) return '#ffbe0b';
    if (score >= 20) return '#ff6b6b';
    return '#ff006e';
  };

  const getScoreLabel = (score) => {
    if (score >= 80) return 'ОТЛИЧНО';
    if (score >= 60) return 'ХОРОШО';
    if (score >= 40) return 'УДОВЛ.';
    if (score >= 20) return 'ПЛОХО';
    return 'КРИТИЧНО';
  };

  const radarData = result?.details ? [
    {
      subject: 'Email',
      A: result.details.email ? Math.max(0, 100 - result.details.email.breach_penalty) : 100,
      fullMark: 100
    },
    {
      subject: 'Username',
      A: result.details.username ? Math.max(0, 100 - result.details.username.spread_penalty) : 100,
      fullMark: 100
    },
    {
      subject: 'Пароль',
      A: result.details.password ? Math.max(0, 100 - result.details.password.total_password_penalty) : 100,
      fullMark: 100
    },
    {
      subject: 'Общий',
      A: result.score,
      fullMark: 100
    },
  ] : [];

  const penaltyData = result?.details ? Object.entries(result.details).map(([key, value]) => {
    let penalty = 0;
    if (key === 'email') penalty = value.breach_penalty || 0;
    if (key === 'username') penalty = value.spread_penalty || 0;
    if (key === 'password') penalty = value.total_password_penalty || 0;
    return { name: key.charAt(0).toUpperCase() + key.slice(1), penalty };
  }) : [];

  return (
    <div className="privacy-score-page">
      <div className="page-header">
        <motion.h1 initial={{ opacity: 0, y: -20 }} animate={{ opacity: 1, y: 0 }}>
          <FaChartLine className="page-icon" /> PRIVACY SCORE
        </motion.h1>
        <motion.p initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.2 }}>
          Комплексная оценка вашего уровня приватности
        </motion.p>
      </div>

      {/* Form */}
      <motion.form
        className="privacy-form"
        onSubmit={calculateScore}
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ delay: 0.3 }}
      >
        <div className="form-row">
          <div className="form-group">
            <label><FaEnvelope /> Email</label>
            <input
              type="email"
              className="input-futuristic"
              placeholder="your@email.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
            />
          </div>
          
          <div className="form-group">
            <label><FaUserSecret /> Username</label>
            <input
              type="text"
              className="input-futuristic"
              placeholder="your_username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
            />
          </div>
          
          <div className="form-group">
            <label><FaKey /> Password</label>
            <input
              type="text"
              className="input-futuristic"
              placeholder="Ваш пароль"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
          </div>
        </div>
        
        <div className="form-actions">
          <button type="submit" className="btn-primary btn-large" disabled={loading}>
            {loading ? <div className="spinner small"></div> : <><FaChartLine /> Рассчитать рейтинг</>}
          </button>
        </div>
      </motion.form>

      <AnimatePresence>
        {error && (
          <motion.div className="error-message" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -20 }}>
            <FaExclamationTriangle /> {error}
          </motion.div>
        )}
      </AnimatePresence>

      <AnimatePresence>
        {result && (
          <motion.div
            className="result-container"
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -30 }}
          >
            {/* Score Circle */}
            <motion.div
              className="score-display"
              initial={{ scale: 0.8, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              transition={{ duration: 0.6, type: 'spring' }}
            >
              <div className="score-circle-large" style={{ borderColor: getScoreColor(result.score) }}>
                <div className="score-content">
                  <div className="score-emoji">{result.emoji}</div>
                  <div className="score-value" style={{ color: getScoreColor(result.score) }}>
                    {result.score}
                  </div>
                  <div className="score-label" style={{ color: getScoreColor(result.score) }}>
                    {getScoreLabel(result.score)}
                  </div>
                </div>
              </div>
              
              <div className="score-description">
                <h3>Ваш рейтинг приватности</h3>
                <p>Штрафов: {result.total_penalty} баллов</p>
              </div>
            </motion.div>

            {/* Radar Chart */}
            <div className="chart-section">
              <h3><FaShieldAlt /> Анализ компонентов</h3>
              <ResponsiveContainer width="100%" height={300}>
                <RadarChart data={radarData}>
                  <PolarGrid stroke="rgba(255,255,255,0.1)" />
                  <PolarAngleAxis dataKey="subject" stroke="#8888aa" />
                  <Radar name="Приватность" dataKey="A" stroke="#00f0ff" fill="rgba(0, 240, 255, 0.2)" />
                </RadarChart>
              </ResponsiveContainer>
            </div>

            {/* Penalty Breakdown */}
            {penaltyData.length > 0 && (
              <div className="chart-section">
                <h3>Штрафы по категориям</h3>
                <ResponsiveContainer width="100%" height={200}>
                  <BarChart data={penaltyData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                    <XAxis dataKey="name" stroke="#8888aa" />
                    <YAxis stroke="#8888aa" />
                    <Tooltip 
                      contentStyle={{ 
                        background: 'rgba(15, 15, 25, 0.95)', 
                        border: '1px solid var(--border)',
                        borderRadius: '8px'
                      }} 
                    />
                    <Bar dataKey="penalty" radius={[8, 8, 0, 0]}>
                      {penaltyData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.penalty > 30 ? '#ff006e' : entry.penalty > 10 ? '#ffbe0b' : '#00f0ff'} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </div>
            )}

            {/* Recommendations */}
            {result.recommendations?.length > 0 && (
              <div className="recommendations-section">
                <h3><FaCheck /> Рекомендации</h3>
                <div className="recommendations-list">
                  {result.recommendations.map((rec, index) => (
                    <motion.div
                      key={index}
                      className="recommendation-item"
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: index * 0.1 }}
                    >
                      <FaCheck />
                      <p>{rec}</p>
                    </motion.div>
                  ))}
                </div>
              </div>
            )}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default PrivacyScore;
