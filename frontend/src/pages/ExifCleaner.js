import React, { useState, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { FaImage, FaUpload, FaBroom, FaCheck, FaTimes, FaExclamationTriangle, FaDownload, FaMapMarkerAlt, FaCamera, FaCalendar, FaInfoCircle } from 'react-icons/fa';
import { useDropzone } from 'react-dropzone';
import axios from 'axios';
import API_URL from '../config';
import './ExifCleaner.css';

const ExifCleaner = () => {
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [loading, setLoading] = useState(false);
  const [analyzeResult, setAnalyzeResult] = useState(null);
  const [cleaning, setCleaning] = useState(false);
  const [error, setError] = useState(null);

  const onDrop = useCallback((acceptedFiles) => {
    const selectedFile = acceptedFiles[0];
    if (selectedFile) {
      setFile(selectedFile);
      setPreview(URL.createObjectURL(selectedFile));
      setAnalyzeResult(null);
      setError(null);
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { 'image/*': [] },
    maxFiles: 1
  });

  const analyzeImage = async () => {
    if (!file) return;
    
    setLoading(true);
    setError(null);
    
    const formData = new FormData();
    formData.append('file', file);
    
    try {
      const response = await axios.post(`${API_URL}/exif/analyze`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      setAnalyzeResult(response.data);
    } catch (err) {
      setError('Ошибка при анализе изображения.');
    } finally {
      setLoading(false);
    }
  };

  const cleanImage = async () => {
    if (!file) return;
    
    setCleaning(true);
    setError(null);
    
    const formData = new FormData();
    formData.append('file', file);
    
    try {
      const response = await axios.post(`${API_URL}/exif/clean`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
        responseType: 'blob'
      });
      
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `cleaned_${file.name}`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (err) {
      setError('Ошибка при очистке изображения.');
    } finally {
      setCleaning(false);
    }
  };

  const resetAll = () => {
    setFile(null);
    setPreview(null);
    setAnalyzeResult(null);
    setError(null);
  };

  return (
    <div className="exif-cleaner-page">
      <div className="page-header">
        <motion.h1 initial={{ opacity: 0, y: -20 }} animate={{ opacity: 1, y: 0 }}>
          <FaImage className="page-icon" /> EXIF CLEANER
        </motion.h1>
        <motion.p initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.2 }}>
          Проанализируйте и удалите метаданные из фотографий перед публикацией
        </motion.p>
      </div>

      {/* Dropzone */}
      <motion.div
        className="dropzone-container"
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ delay: 0.3 }}
      >
        <div {...getRootProps()} className={`dropzone ${isDragActive ? 'active' : ''}`}>
          <input {...getInputProps()} />
          <div className="dropzone-content">
            <FaUpload className="dropzone-icon" />
            <h3>{isDragActive ? 'Отпустите файл здесь' : 'Перетащите изображение сюда'}</h3>
            <p>или нажмите для выбора файла</p>
          </div>
        </div>

        {file && (
          <motion.div className="file-info" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
            <div className="file-preview">
              <img src={preview} alt="Preview" />
            </div>
            <div className="file-details">
              <h4>{file.name}</h4>
              <p>{(file.size / 1024).toFixed(2)} KB</p>
            </div>
            <div className="file-actions">
              <button className="btn-primary" onClick={analyzeImage} disabled={loading}>
                {loading ? <div className="spinner small"></div> : <><FaInfoCircle /> Анализировать</>}
              </button>
              {analyzeResult && (
                <button className="btn-secondary" onClick={cleanImage} disabled={cleaning}>
                  {cleaning ? <div className="spinner small"></div> : <><FaBroom /> Очистить EXIF</>}
                </button>
              )}
              <button className="btn-reset" onClick={resetAll}>
                <FaTimes /> Сбросить
              </button>
            </div>
          </motion.div>
        )}
      </motion.div>

      <AnimatePresence>
        {error && (
          <motion.div className="error-message" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -20 }}>
            <FaExclamationTriangle /> {error}
          </motion.div>
        )}
      </AnimatePresence>

      <AnimatePresence>
        {analyzeResult && (
          <motion.div
            className="result-container"
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -30 }}
          >
            {/* Risk Level */}
            <div className="risk-banner" style={{ borderColor: getRiskColor(analyzeResult.risk_level) }}>
              <div className="risk-icon" style={{ color: getRiskColor(analyzeResult.risk_level) }}>
                {getRiskIcon(analyzeResult.risk_level)}
              </div>
              <div className="risk-info">
                <h3 style={{ color: getRiskColor(analyzeResult.risk_level) }}>
                  Уровень утечки: {analyzeResult.risk_level.toUpperCase()}
                </h3>
                <p>Найдено {analyzeResult.exif_count} EXIF-записей</p>
              </div>
            </div>

            {/* Privacy Risks */}
            {analyzeResult.privacy_risks?.length > 0 && (
              <div className="privacy-risks-section">
                <h3><FaExclamationTriangle /> Обнаруженные риски</h3>
                <div className="risks-list">
                  {analyzeResult.privacy_risks.map((risk, index) => (
                    <motion.div
                      key={index}
                      className="risk-item"
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: index * 0.1 }}
                    >
                      <FaExclamationTriangle />
                      <p>{risk}</p>
                    </motion.div>
                  ))}
                </div>
              </div>
            )}

            {/* EXIF Data */}
            <div className="exif-data-section">
              <h3><FaInfoCircle /> EXIF-данные</h3>
              <div className="exif-grid">
                {analyzeResult.exif_data?.GPS && (
                  <div className="exif-card gps">
                    <FaMapMarkerAlt className="exif-icon" />
                    <h4>GPS-координаты</h4>
                    <p>Широта: {analyzeResult.exif_data.GPS.latitude?.toFixed(6)}</p>
                    <p>Долгота: {analyzeResult.exif_data.GPS.longitude?.toFixed(6)}</p>
                    {analyzeResult.exif_data.GPS.altitude && (
                      <p>Высота: {analyzeResult.exif_data.GPS.altitude}м</p>
                    )}
                  </div>
                )}
                
                {analyzeResult.exif_data.Model && (
                  <div className="exif-card">
                    <FaCamera className="exif-icon" />
                    <h4>Камера</h4>
                    <p>{analyzeResult.exif_data.Model}</p>
                    {analyzeResult.exif_data.Make && <p>Производитель: {analyzeResult.exif_data.Make}</p>}
                  </div>
                )}
                
                {(analyzeResult.exif_data.DateTime || analyzeResult.exif_data.DateTimeOriginal) && (
                  <div className="exif-card">
                    <FaCalendar className="exif-icon" />
                    <h4>Дата и время</h4>
                    <p>{analyzeResult.exif_data.DateTimeOriginal || analyzeResult.exif_data.DateTime}</p>
                  </div>
                )}

                {Object.keys(analyzeResult.exif_data)
                  .filter(key => !['GPS', 'Model', 'Make', 'DateTime', 'DateTimeOriginal', 'Software'].includes(key))
                  .slice(0, 6)
                  .map((key, index) => (
                    <div className="exif-card" key={index}>
                      <FaInfoCircle className="exif-icon" />
                      <h4>{key}</h4>
                      <p className="exif-value">{analyzeResult.exif_data[key]}</p>
                    </div>
                  ))
                }
              </div>
            </div>

            {/* Clean CTA */}
            <motion.div
              className="clean-cta"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.5 }}
            >
              <p>Удалите все метаданные перед публикацией фотографии</p>
              <button className="btn-primary btn-large" onClick={cleanImage} disabled={cleaning}>
                {cleaning ? <div className="spinner small"></div> : <><FaBroom /> Очистить и скачать</>}
              </button>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

const getRiskColor = (risk) => {
  switch (risk?.toLowerCase()) {
    case 'высокий': return '#ff006e';
    case 'средний': return '#ffbe0b';
    case 'низкий': return '#00ff88';
    default: return '#8888aa';
  }
};

const getRiskIcon = (risk) => {
  switch (risk?.toLowerCase()) {
    case 'высокий': return <FaTimes />;
    case 'средний': return <FaExclamationTriangle />;
    case 'низкий': return <FaCheck />;
    default: return null;
  }
};

export default ExifCleaner;
