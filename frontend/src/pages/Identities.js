import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { FaDatabase, FaPlus, FaEdit, FaTrash, FaCopy, FaCheck, FaExclamationTriangle, FaUser, FaSave } from 'react-icons/fa';
import axios from 'axios';
import API_URL from '../config';
import './Identities.css';

const Identities = () => {
  const [identities, setIdentities] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [editingId, setEditingId] = useState(null);
  const [copiedId, setCopiedId] = useState(null);
  const [error, setError] = useState(null);
  const [formData, setFormData] = useState({
    label: '',
    name: '',
    email: '',
    phone: '',
    birthdate: '',
    address: '',
    username: '',
    password: ''
  });

  useEffect(() => {
    fetchIdentities();
  }, []);

  const fetchIdentities = async () => {
    try {
      const response = await axios.get(`${API_URL}/identities/`);
      console.log('Загружены личности:', response.data);
      setIdentities(response.data);
    } catch (err) {
      console.error('Ошибка загрузки:', err);
      setError('Ошибка при загрузке личностей');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);

    const payload = { ...formData };
    // Удаляем пустые поля, чтобы бэкенд сгенерировал их сам
    Object.keys(payload).forEach(key => {
      if (payload[key] === '') delete payload[key];
    });

    console.log('Отправляем:', payload);

    try {
      if (editingId) {
        await axios.put(`${API_URL}/identities/${editingId}`, payload);
      } else {
        const resp = await axios.post(`${API_URL}/identities/`, payload);
        console.log('Ответ сервера:', resp.data);
      }
      await fetchIdentities();
      resetForm();
    } catch (err) {
      console.error('Ошибка при сохранении:', err.response?.data || err.message);
      setError(err.response?.data?.detail || 'Ошибка при сохранении личности');
    }
  };

  const handleEdit = (identity) => {
    setEditingId(identity.id);
    setFormData({
      label: identity.label || '',
      name: identity.name || '',
      email: identity.email || '',
      phone: identity.phone || '',
      birthdate: identity.birthdate || '',
      address: identity.address || '',
      username: identity.username || '',
      password: identity.password || ''
    });
    setShowForm(true);
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Удалить эту личность?')) return;
    
    try {
      await axios.delete(`${API_URL}/identities/${id}`);
      fetchIdentities();
    } catch (err) {
      setError('Ошибка при удалении');
    }
  };

  const resetForm = () => {
    setShowForm(false);
    setEditingId(null);
    setFormData({
      label: '',
      name: '',
      email: '',
      phone: '',
      birthdate: '',
      address: '',
      username: '',
      password: ''
    });
  };

  const copyToClipboard = (text, id) => {
    navigator.clipboard.writeText(text);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  const getStrengthBadge = (strength) => {
    switch (strength?.toLowerCase()) {
      case 'сильный': return <span className="badge badge-success">{strength}</span>;
      case 'средний': return <span className="badge badge-warning">{strength}</span>;
      case 'слабый': return <span className="badge badge-danger">{strength}</span>;
      default: return <span className="badge badge-info">{strength || 'N/A'}</span>;
    }
  };

  return (
    <div className="identities-page">
      <div className="page-header">
        <motion.h1 initial={{ opacity: 0, y: -20 }} animate={{ opacity: 1, y: 0 }}>
          <FaDatabase className="page-icon" /> IDENTITY MANAGER
        </motion.h1>
        <motion.p initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.2 }}>
          Управление альтернативными личностями. Создавайте и храните фейковые профили
        </motion.p>
      </div>

      <motion.div
        className="actions-bar"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
      >
        <button className="btn-primary" onClick={() => setShowForm(true)}>
          <FaPlus /> Создать личность
        </button>
        <span className="identities-count">Всего: {identities.length}</span>
      </motion.div>

      <AnimatePresence>
        {error && (
          <motion.div className="error-message" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -20 }}>
            <FaExclamationTriangle /> {error}
          </motion.div>
        )}
      </AnimatePresence>

      {/* Form Modal */}
      <AnimatePresence>
        {showForm && (
          <motion.div
            className="form-overlay"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={resetForm}
          >
            <motion.div
              className="form-modal"
              initial={{ opacity: 0, scale: 0.9, y: 30 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.9, y: 30 }}
              onClick={(e) => e.stopPropagation()}
            >
              <div className="form-header">
                <h2>{editingId ? 'Редактировать личность' : 'Новая личность'}</h2>
                <button className="close-btn" onClick={resetForm}>
                  <FaTrash style={{ fontSize: '12px' }} /> Отмена
                </button>
              </div>
              
              <form onSubmit={handleSubmit} className="identity-form">
                <div className="form-grid">
                  <div className="form-group">
                    <label>Название *</label>
                    <input
                      type="text"
                      className="input-futuristic"
                      placeholder="Например: Для форума X"
                      value={formData.label}
                      onChange={(e) => setFormData({...formData, label: e.target.value})}
                      required
                    />
                  </div>
                  
                  <div className="form-group">
                    <label>Имя</label>
                    <input
                      type="text"
                      className="input-futuristic"
                      placeholder="Оставьте пустым для авто-генерации"
                      value={formData.name}
                      onChange={(e) => setFormData({...formData, name: e.target.value})}
                    />
                  </div>
                  
                  <div className="form-group">
                    <label>Email</label>
                    <input
                      type="email"
                      className="input-futuristic"
                      placeholder="Авто-генерация если пусто"
                      value={formData.email}
                      onChange={(e) => setFormData({...formData, email: e.target.value})}
                    />
                  </div>
                  
                  <div className="form-group">
                    <label>Телефон</label>
                    <input
                      type="tel"
                      className="input-futuristic"
                      value={formData.phone}
                      onChange={(e) => setFormData({...formData, phone: e.target.value})}
                    />
                  </div>
                  
                  <div className="form-group">
                    <label>Дата рождения</label>
                    <input
                      type="date"
                      className="input-futuristic"
                      value={formData.birthdate}
                      onChange={(e) => setFormData({...formData, birthdate: e.target.value})}
                    />
                  </div>
                  
                  <div className="form-group full-width">
                    <label>Адрес</label>
                    <input
                      type="text"
                      className="input-futuristic"
                      value={formData.address}
                      onChange={(e) => setFormData({...formData, address: e.target.value})}
                    />
                  </div>
                  
                  <div className="form-group">
                    <label>Username</label>
                    <input
                      type="text"
                      className="input-futuristic"
                      value={formData.username}
                      onChange={(e) => setFormData({...formData, username: e.target.value})}
                    />
                  </div>
                  
                  <div className="form-group">
                    <label>Пароль</label>
                    <input
                      type="text"
                      className="input-futuristic"
                      value={formData.password}
                      onChange={(e) => setFormData({...formData, password: e.target.value})}
                    />
                  </div>
                </div>
                
                <div className="form-actions">
                  <button type="submit" className="btn-primary">
                    <FaSave /> {editingId ? 'Сохранить' : 'Создать'}
                  </button>
                  <button type="button" className="btn-secondary" onClick={resetForm}>
                    Отмена
                  </button>
                </div>
              </form>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Identities List */}
      {loading ? (
        <div className="loading-container">
          <div className="spinner"></div>
          <p>Загрузка...</p>
        </div>
      ) : identities.length === 0 ? (
        <motion.div className="empty-state" initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
          <FaDatabase className="empty-icon" />
          <h3>Нет сохранённых личностей</h3>
          <p>Создайте первую фейковую личность для безопасной регистрации</p>
          <button className="btn-primary" onClick={() => setShowForm(true)}>
            <FaPlus /> Создать
          </button>
        </motion.div>
      ) : (
        <div className="identities-grid">
          {identities.map((identity, index) => (
            <motion.div
              key={identity.id}
              className="identity-list-card"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.05 }}
            >
              <div className="card-header">
                <div className="card-title">
                  <FaUser />
                  <h3>{identity.label}</h3>
                </div>
                <div className="card-actions">
                  <button className="icon-btn" onClick={() => handleEdit(identity)}>
                    <FaEdit />
                  </button>
                  <button className="icon-btn danger" onClick={() => handleDelete(identity.id)}>
                    <FaTrash />
                  </button>
                </div>
              </div>
              
              <div className="card-body">
                <div className="info-row">
                  <span className="info-label">Имя:</span>
                  <span className="info-value">{identity.name}</span>
                </div>
                <div className="info-row">
                  <span className="info-label">Email:</span>
                  <span className="info-value">{identity.email}</span>
                  <button className="copy-small" onClick={() => copyToClipboard(identity.email, `email-${identity.id}`)}>
                    {copiedId === `email-${identity.id}` ? <FaCheck /> : <FaCopy />}
                  </button>
                </div>
                <div className="info-row">
                  <span className="info-label">Username:</span>
                  <span className="info-value">{identity.username}</span>
                </div>
                <div className="info-row">
                  <span className="info-label">Пароль:</span>
                  {getStrengthBadge(identity.password_strength)}
                </div>
                <div className="info-row">
                  <span className="info-label">Создана:</span>
                  <span className="info-value">{new Date(identity.created_at).toLocaleDateString('ru-RU')}</span>
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      )}
    </div>
  );
};

export default Identities;
