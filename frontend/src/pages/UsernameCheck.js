import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { FaSearch, FaCheck, FaTimes, FaExclamationTriangle, FaExternalLinkAlt, FaUser, FaPhone, FaUserSecret, FaInfoCircle } from 'react-icons/fa';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend } from 'recharts';
import axios from 'axios';
import API_URL from '../config';
import './UsernameCheck.css';

const UsernameCheck = () => {
  const [username, setUsername] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [filter, setFilter] = useState('all'); // all, found, not_found

  const checkUsername = async (e) => {
    e.preventDefault();
    if (!username.trim()) return;
    
    setLoading(true);
    setError(null);
    setResult(null);
    
    try {
      const response = await axios.get(`${API_URL}/check/username/${encodeURIComponent(username)}`);
      setResult(response.data);
    } catch (err) {
      setError('Ошибка при проверке username. Попробуйте позже.');
    } finally {
      setLoading(false);
    }
  };

  const getFilteredSites = () => {
    if (!result) return [];
    switch (filter) {
      case 'found': return result.found || [];
      case 'not_found': return result.not_found || [];
      default: return [...(result.found || []), ...(result.not_found || [])];
    }
  };

  const pieData = result ? [
    { name: 'Найдено', value: result.found_count, color: '#00ff88' },
    { name: 'Не найдено', value: result.not_found_count, color: '#00f0ff' },
    { name: 'Ошибки', value: result.error_count, color: '#ff006e' },
  ].filter(item => item.value > 0) : [];

  return (
    <div className="username-check-page">
      <div className="page-header">
        <motion.h1 initial={{ opacity: 0, y: -20 }} animate={{ opacity: 1, y: 0 }}>
          <FaSearch className="page-icon" /> USERNAME OSINT
        </motion.h1>
        <motion.p initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.2 }}>
          Проверка никнейма на 48+ платформах. Узнайте, где «засветился» ваш username
        </motion.p>
      </div>

      <motion.form
        className="search-form"
        onSubmit={checkUsername}
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ delay: 0.3 }}
      >
        <div className="input-group">
          <input
            type="text"
            className="input-futuristic"
            placeholder="Введите username для проверки..."
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            required
          />
          <button type="submit" className="btn-primary" disabled={loading}>
            {loading ? <div className="spinner small"></div> : <><FaSearch /> Проверить</>}
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
            {/* Summary Cards */}
            <div className="summary-cards">
              <motion.div className="summary-card found" initial={{ opacity: 0, scale: 0.9 }} animate={{ opacity: 1, scale: 1 }} transition={{ delay: 0.1 }}>
                <div className="card-icon"><FaCheck /></div>
                <div className="card-info">
                  <h3>{result.found_count}</h3>
                  <p>Найдено</p>
                </div>
              </motion.div>
              
              <motion.div className="summary-card not-found" initial={{ opacity: 0, scale: 0.9 }} animate={{ opacity: 1, scale: 1 }} transition={{ delay: 0.2 }}>
                <div className="card-icon"><FaTimes /></div>
                <div className="card-info">
                  <h3>{result.not_found_count}</h3>
                  <p>Не найдено</p>
                </div>
              </motion.div>
              
              <motion.div className="summary-card errors" initial={{ opacity: 0, scale: 0.9 }} animate={{ opacity: 1, scale: 1 }} transition={{ delay: 0.3 }}>
                <div className="card-icon"><FaExclamationTriangle /></div>
                <div className="card-info">
                  <h3>{result.error_count}</h3>
                  <p>Ошибки</p>
                </div>
              </motion.div>
            </div>

            {/* Pie Chart */}
            <div className="chart-section">
              <h3>Распределение результатов</h3>
              <ResponsiveContainer width="100%" height={250}>
                <PieChart>
                  <Pie
                    data={pieData}
                    cx="50%"
                    cy="50%"
                    innerRadius={60}
                    outerRadius={90}
                    paddingAngle={5}
                    dataKey="value"
                  >
                    {pieData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip 
                    contentStyle={{ 
                      background: 'rgba(15, 15, 25, 0.95)', 
                      border: '1px solid var(--border)',
                      borderRadius: '8px'
                    }}
                  />
                  <Legend />
                </PieChart>
              </ResponsiveContainer>
            </div>

            {/* Filter Tabs */}
            <div className="filter-tabs">
              <button className={`filter-tab ${filter === 'all' ? 'active' : ''}`} onClick={() => setFilter('all')}>
                Все ({result.total_sites_checked})
              </button>
              <button className={`filter-tab ${filter === 'found' ? 'active' : ''}`} onClick={() => setFilter('found')}>
                Найдено ({result.found_count})
              </button>
              <button className={`filter-tab ${filter === 'not_found' ? 'active' : ''}`} onClick={() => setFilter('not_found')}>
                Не найдено ({result.not_found_count})
              </button>
            </div>

            {/* Sites List */}
            <div className="sites-section">
              <h3>Результаты по платформам</h3>
              <div className="sites-list">
                {getFilteredSites().map((site, index) => (
                  <motion.div
                    key={index}
                    className={`site-item ${site.exists ? 'found' : 'not-found'}`}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: index * 0.02 }}
                  >
                    <div className="site-status">
                      {site.exists ? <FaCheck className="status-icon" /> : <FaTimes className="status-icon" />}
                    </div>
                    <div className="site-info">
                      <h4>{site.site}</h4>
                      {site.error && <p className="site-error">{site.error}</p>}

                      {/* OSINT: Личная информация */}
                      {site.personal_info && (
                        <div className="personal-info">
                          <div className="personal-info-header">
                            <FaUserSecret /> Обнаружены данные:
                          </div>
                          <div className="personal-info-grid">
                            {site.personal_info.name && (
                              <div className="info-item">
                                <FaUser className="info-icon" />
                                <div>
                                  <span className="info-label">Имя:</span>
                                  <span className="info-value">{site.personal_info.name}</span>
                                </div>
                              </div>
                            )}
                            {site.personal_info.phone && (
                              <div className="info-item phone-highlight">
                                <FaPhone className="info-icon" />
                                <div>
                                  <span className="info-label">Телефон:</span>
                                  <span className="info-value">{site.personal_info.phone}</span>
                                </div>
                              </div>
                            )}
                            {site.personal_info.bio && (
                              <div className="info-item">
                                <FaInfoCircle className="info-icon" />
                                <div>
                                  <span className="info-label">Bio:</span>
                                  <span className="info-value">{site.personal_info.bio}</span>
                                </div>
                              </div>
                            )}
                          </div>
                        </div>
                      )}
                    </div>
                    <a href={site.url} target="_blank" rel="noopener noreferrer" className="site-link">
                      <FaExternalLinkAlt />
                    </a>
                  </motion.div>
                ))}
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default UsernameCheck;
