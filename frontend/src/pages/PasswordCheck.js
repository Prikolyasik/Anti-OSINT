import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { FaKey, FaEye, FaEyeSlash, FaCheck, FaTimes, FaExclamationTriangle } from 'react-icons/fa';
import { RadarChart, PolarGrid, PolarAngleAxis, Radar, ResponsiveContainer } from 'recharts';
import axios from 'axios';
import './PasswordCheck.css';

const API_URL = 'http://localhost:8000';

const PasswordCheck = () => {
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const checkPassword = async (e) => {
    e.preventDefault();
    if (!password.trim()) return;
    
    setLoading(true);
    setError(null);
    setResult(null);
    
    try {
      const response = await axios.post(`${API_URL}/check/password`, { password });
      setResult(response.data);
    } catch (err) {
      setError('Ошибка при проверке пароля. Попробуйте позже.');
    } finally {
      setLoading(false);
    }
  };

  const getStrengthColor = (strength) => {
    switch (strength?.toLowerCase()) {
      case 'отличный': return '#00ff88';
      case 'хороший': return '#00f0ff';
      case 'средний': return '#ffbe0b';
      case 'слабый': return '#ff6b6b';
      case 'очень слабый': return '#ff006e';
      default: return '#8888aa';
    }
  };

  const getRiskColor = (risk) => {
    switch (risk?.toLowerCase()) {
      case 'безопасный': return '#00ff88';
      case 'низкий': return '#00f0ff';
      case 'средний': return '#ffbe0b';
      case 'высокий': return '#ff6b6b';
      case 'критический': return '#ff006e';
      default: return '#8888aa';
    }
  };

  const radarData = result ? [
    { subject: 'Длина', A: Math.min(result.strength.length / 16 * 100, 100), fullMark: 100 },
    { subject: 'Строчные', A: /[a-z]/.test(password) ? 100 : 0, fullMark: 100 },
    { subject: 'Заглавные', A: /[A-Z]/.test(password) ? 100 : 0, fullMark: 100 },
    { subject: 'Цифры', A: /\d/.test(password) ? 100 : 0, fullMark: 100 },
    { subject: 'Спецсимволы', A: /[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]/.test(password) ? 100 : 0, fullMark: 100 },
    { subject: 'Безопасность', A: result.strength.score, fullMark: 100 },
  ] : [];

  return (
    <div className="password-check-page">
      <div className="page-header">
        <motion.h1 initial={{ opacity: 0, y: -20 }} animate={{ opacity: 1, y: 0 }}>
          <FaKey className="page-icon" /> PASSWORD CHECK
        </motion.h1>
        <motion.p initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.2 }}>
          Проверьте надёжность пароля и наличие в базах утечек (k-Anonymity)
        </motion.p>
      </div>

      <motion.form
        className="search-form"
        onSubmit={checkPassword}
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ delay: 0.3 }}
      >
        <div className="input-group password-input-group">
          <div className="input-wrapper">
            <input
              type={showPassword ? 'text' : 'password'}
              className="input-futuristic"
              placeholder="Введите пароль для проверки..."
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
            <button
              type="button"
              className="toggle-password-btn"
              onClick={() => setShowPassword(!showPassword)}
            >
              {showPassword ? <FaEyeSlash /> : <FaEye />}
            </button>
          </div>
          <button type="submit" className="btn-primary" disabled={loading}>
            {loading ? <div className="spinner small"></div> : <><FaKey /> Проверить</>}
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
            {/* Strength Banner */}
            <motion.div
              className="strength-banner"
              style={{ borderColor: getStrengthColor(result.strength.strength) }}
            >
              <div className="strength-info">
                <h3 style={{ color: getStrengthColor(result.strength.strength) }}>
                  Надёжность: {result.strength.strength.toUpperCase()}
                </h3>
                <div className="strength-score">
                  <div className="score-circle" style={{ borderColor: getStrengthColor(result.strength.strength) }}>
                    <span style={{ color: getStrengthColor(result.strength.strength) }}>
                      {result.strength.score}
                    </span>
                  </div>
                  <p>Баллов: {result.strength.score}/100</p>
                </div>
              </div>
            </motion.div>

            {/* Radar Chart */}
            <div className="chart-section">
              <h3>Анализ пароля</h3>
              <ResponsiveContainer width="100%" height={300}>
                <RadarChart data={radarData}>
                  <PolarGrid stroke="rgba(255,255,255,0.1)" />
                  <PolarAngleAxis dataKey="subject" stroke="#8888aa" />
                  <Radar name="Параметры" dataKey="A" stroke="#00f0ff" fill="rgba(0, 240, 255, 0.2)" />
                </RadarChart>
              </ResponsiveContainer>
            </div>

            {/* Issues & Suggestions */}
            <div className="details-grid">
              {result.strength.issues?.length > 0 && (
                <div className="detail-section">
                  <h3><FaTimes className="detail-icon" /> Проблемы</h3>
                  <ul className="issue-list">
                    {result.strength.issues.map((issue, index) => (
                      <li key={index}><FaTimes /> {issue}</li>
                    ))}
                  </ul>
                </div>
              )}

              {result.strength.suggestions?.length > 0 && (
                <div className="detail-section">
                  <h3><FaCheck className="detail-icon success" /> Рекомендации</h3>
                  <ul className="suggestion-list">
                    {result.strength.suggestions.map((suggestion, index) => (
                      <li key={index}><FaCheck /> {suggestion}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>

            {/* HIBP Result */}
            <div className="hibp-section">
              <h3><FaKey className="detail-icon" /> Have I Been Pwned</h3>
              <div className="hibp-result">
                <div className="hibp-status" style={{ color: getRiskColor(result.hibp.risk_level) }}>
                  {result.hibp.found ? <FaTimes className="hibp-icon" /> : <FaCheck className="hibp-icon success" />}
                  <div>
                    <h4 style={{ color: getRiskColor(result.hibp.risk_level) }}>
                      {result.hibp.found ? 'НАЙДЕН В УТЕЧКАХ' : 'НЕ НАЙДЕН'}
                    </h4>
                    {result.hibp.found && (
                      <p>Встречается в {result.hibp.pwned_count.toLocaleString()} утечках</p>
                    )}
                    <p className="hibp-note">{result.hibp.k_anonymity_note}</p>
                  </div>
                </div>
              </div>
              <div className="risk-level" style={{ borderColor: getRiskColor(result.hibp.risk_level) }}>
                Уровень риска: <strong style={{ color: getRiskColor(result.hibp.risk_level) }}>
                  {result.hibp.risk_level.toUpperCase()}
                </strong>
              </div>
            </div>

            {/* Recommendation */}
            <motion.div
              className="final-recommendation"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.5 }}
            >
              <p>{result.recommendation}</p>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default PasswordCheck;
