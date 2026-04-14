import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { FaSearch, FaExclamationTriangle, FaCheckCircle, FaTimesCircle } from 'react-icons/fa';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts';
import axios from 'axios';
import './EmailCheck.css';

const API_URL = 'http://localhost:8000';

const EmailCheck = () => {
  const [email, setEmail] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const checkEmail = async (e) => {
    e.preventDefault();
    if (!email.trim()) return;
    
    setLoading(true);
    setError(null);
    setResult(null);
    
    try {
      const response = await axios.get(`${API_URL}/check/email/${encodeURIComponent(email)}`);
      setResult(response.data);
    } catch (err) {
      setError('Ошибка при проверке email. Попробуйте позже.');
    } finally {
      setLoading(false);
    }
  };

  const getRiskColor = (risk) => {
    switch (risk?.toLowerCase()) {
      case 'низкий': return '#00ff88';
      case 'средний': return '#ffbe0b';
      case 'высокий': return '#ff006e';
      default: return '#8888aa';
    }
  };

  const getRiskIcon = (risk) => {
    switch (risk?.toLowerCase()) {
      case 'низкий': return <FaCheckCircle />;
      case 'средний': return <FaExclamationTriangle />;
      case 'высокий': return <FaTimesCircle />;
      default: return null;
    }
  };

  const chartData = result ? [
    { name: 'Утечек', value: result.count, fill: getRiskColor(result.risk) }
  ] : [];

  return (
    <div className="email-check-page">
      <div className="page-header">
        <motion.h1
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
        >
          <FaSearch className="page-icon" /> EMAIL BREACH CHECK
        </motion.h1>
        <motion.p
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.2 }}
        >
          Проверьте, попал ли ваш email в известные утечки данных
        </motion.p>
      </div>

      <motion.form
        className="search-form"
        onSubmit={checkEmail}
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ delay: 0.3 }}
      >
        <div className="input-group">
          <input
            type="email"
            className="input-futuristic"
            placeholder="Введите email для проверки..."
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
          <button type="submit" className="btn-primary" disabled={loading}>
            {loading ? <div className="spinner small"></div> : <><FaSearch /> Проверить</>}
          </button>
        </div>
      </motion.form>

      <AnimatePresence>
        {error && (
          <motion.div
            className="error-message"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
          >
            <FaTimesCircle /> {error}
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
            transition={{ duration: 0.5 }}
          >
            {/* Risk Banner */}
            <motion.div
              className="risk-banner"
              style={{ borderColor: getRiskColor(result.risk) }}
            >
              <div className="risk-icon" style={{ color: getRiskColor(result.risk) }}>
                {getRiskIcon(result.risk)}
              </div>
              <div className="risk-info">
                <h3 style={{ color: getRiskColor(result.risk) }}>
                  РИСК: {result.risk?.toUpperCase()}
                </h3>
                <p>Найдено <strong>{result.count}</strong> утечек для email <strong>{result.email}</strong></p>
              </div>
            </motion.div>

            {/* Chart */}
            {result.count > 0 && (
              <div className="chart-section">
                <h3>Статистика утечек</h3>
                <ResponsiveContainer width="100%" height={200}>
                  <BarChart data={chartData}>
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
                    <Bar dataKey="value" radius={[8, 8, 0, 0]}>
                      <Cell fill={getRiskColor(result.risk)} />
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </div>
            )}

            {/* Breaches List */}
            {result.breaches?.length > 0 && (
              <div className="breaches-section">
                <h3>Затронутые базы данных</h3>
                <div className="breaches-grid">
                  {result.breaches.map((breach, index) => (
                    <motion.div
                      key={index}
                      className="breach-card"
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: index * 0.05 }}
                    >
                      <div className="breach-number">{index + 1}</div>
                      <div className="breach-info">
                        <h4>{breach.name || breach}</h4>
                        {breach.date && <p className="breach-date">Дата: {breach.date}</p>}
                      </div>
                    </motion.div>
                  ))}
                </div>
              </div>
            )}

            {/* Success Message */}
            {result.count === 0 && (
              <motion.div
                className="success-message"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.3 }}
              >
                <FaCheckCircle className="success-icon" />
                <h3>Отличные новости!</h3>
                <p>Email не найден в известных утечках данных. Продолжайте следить за приватностью!</p>
              </motion.div>
            )}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default EmailCheck;
