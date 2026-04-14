import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { FaRobot, FaCopy, FaCheck, FaUser, FaEnvelope, FaPhone, FaBirthdayCake, FaMapMarkerAlt, FaUserCircle, FaKey } from 'react-icons/fa';
import axios from 'axios';
import API_URL from '../config';
import './FakeGenerator.css';

const FakeGenerator = () => {
  const [identity, setIdentity] = useState(null);
  const [loading, setLoading] = useState(false);
  const [copiedField, setCopiedField] = useState(null);
  const [error, setError] = useState(null);

  const generateIdentity = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await axios.get(`${API_URL}/generate/identity`);
      setIdentity(response.data);
    } catch (err) {
      setError('Ошибка при генерации личности.');
    } finally {
      setLoading(false);
    }
  };

  const copyToClipboard = (text, field) => {
    navigator.clipboard.writeText(text);
    setCopiedField(field);
    setTimeout(() => setCopiedField(null), 2000);
  };

  const fields = identity ? [
    { icon: <FaUser />, label: 'Имя', value: identity.name, field: 'name' },
    { icon: <FaEnvelope />, label: 'Email', value: identity.email, field: 'email' },
    { icon: <FaPhone />, label: 'Телефон', value: identity.phone, field: 'phone' },
    { icon: <FaBirthdayCake />, label: 'Дата рождения', value: identity.birthdate, field: 'birthdate' },
    { icon: <FaMapMarkerAlt />, label: 'Адрес', value: identity.address, field: 'address' },
    { icon: <FaUserCircle />, label: 'Username', value: identity.username, field: 'username' },
    { icon: <FaKey />, label: 'Пароль', value: identity.password, field: 'password' },
  ] : [];

  return (
    <div className="fake-generator-page">
      <div className="page-header">
        <motion.h1 initial={{ opacity: 0, y: -20 }} animate={{ opacity: 1, y: 0 }}>
          <FaRobot className="page-icon" /> FAKE GENERATOR
        </motion.h1>
        <motion.p initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.2 }}>
          Генерация фейковых личностей для безопасной регистрации на сервисах
        </motion.p>
      </div>

      {/* Generate Button */}
      <motion.div
        className="generate-section"
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ delay: 0.3 }}
      >
        <button className="btn-primary btn-large" onClick={generateIdentity} disabled={loading}>
          {loading ? (
            <div className="spinner small"></div>
          ) : (
            <><FaRobot /> Сгенерировать личность</>
          )}
        </button>
      </motion.div>

      <AnimatePresence>
        {error && (
          <motion.div className="error-message" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -20 }}>
            {error}
          </motion.div>
        )}
      </AnimatePresence>

      <AnimatePresence>
        {identity && (
          <motion.div
            className="result-container"
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -30 }}
          >
            <div className="identity-header">
              <h2>Сгенерированная личность</h2>
              <button className="btn-secondary" onClick={generateIdentity}>
                <FaRobot /> Новая
              </button>
            </div>

            <div className="identity-grid">
              {fields.map((field, index) => (
                <motion.div
                  key={index}
                  className="identity-card"
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.08 }}
                >
                  <div className="identity-card-header">
                    <div className="card-icon">{field.icon}</div>
                    <h4>{field.label}</h4>
                  </div>
                  <div className="identity-card-body">
                    <div className="field-value">{field.value}</div>
                    <button
                      className="copy-btn"
                      onClick={() => copyToClipboard(field.value, field.field)}
                    >
                      {copiedField === field.field ? <FaCheck /> : <FaCopy />}
                    </button>
                  </div>
                </motion.div>
              ))}
            </div>

            {/* Warning */}
            <motion.div
              className="warning-notice"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.8 }}
            >
              <p>⚠️ Используйте фейковые данные ответственно. Не используйте для мошенничества или незаконной деятельности.</p>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default FakeGenerator;
