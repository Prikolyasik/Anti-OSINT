import React from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { 
  FaSearch, 
  FaUserSecret, 
  FaKey, 
  FaImage, 
  FaDatabase, 
  FaChartLine,
  FaRobot,
  FaArrowRight,
  FaShieldAlt
} from 'react-icons/fa';
import './Homepage.css';

const Homepage = () => {
  const features = [
    {
      icon: <FaSearch />,
      title: 'Email Breach Check',
      description: 'Проверьте, попал ли ваш email в известные утечки данных',
      path: '/email-check',
      color: '#00f0ff'
    },
    {
      icon: <FaUserSecret />,
      title: 'Username OSINT',
      description: 'Узнайте, на каких платформах зарегистрирован никнейм',
      path: '/username-check',
      color: '#7b2ff7'
    },
    {
      icon: <FaKey />,
      title: 'Password Check',
      description: 'Оцените надёжность пароля и проверьте его по базе утечек',
      path: '/password-check',
      color: '#ff006e'
    },
    {
      icon: <FaImage />,
      title: 'EXIF Cleaner',
      description: 'Удалите метаданные из фотографий перед публикацией',
      path: '/exif-cleaner',
      color: '#00ff88'
    },
    {
      icon: <FaRobot />,
      title: 'Fake Generator',
      description: 'Генерация фейковых личностей для безопасной регистрации',
      path: '/fake-generator',
      color: '#ffbe0b'
    },
    {
      icon: <FaDatabase />,
      title: 'Identity Manager',
      description: 'Управление альтернативными личностями в одном месте',
      path: '/identities',
      color: '#00f0ff'
    },
    {
      icon: <FaChartLine />,
      title: 'Privacy Score',
      description: 'Комплексная оценка вашего уровня приватности',
      path: '/privacy-score',
      color: '#7b2ff7'
    },
  ];

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: { staggerChildren: 0.1 }
    }
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 30 },
    visible: { opacity: 1, y: 0 }
  };

  return (
    <div className="homepage">
      {/* Hero Section */}
      <section className="hero-section">
        <div className="hero-content">
          <motion.div
            initial={{ opacity: 0, y: 50 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            className="hero-badge"
          >
            <FaShieldAlt /> ЗАЩИТА ЦИФРОВОГО СЛЕДА
          </motion.div>
          
          <motion.h1
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.8, delay: 0.2 }}
            className="hero-title glitch"
            data-text="ANTI-OSINT"
          >
            ANTI-OSINT
          </motion.h1>
          
          <motion.p
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.8, delay: 0.4 }}
            className="hero-subtitle"
          >
            Комплексный инструментарий для защиты вашей цифровой приватности.
            <br />
            Проверяйте, контролируйте и защищайте свои персональные данные.
          </motion.p>
          
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.6 }}
            className="hero-cta"
          >
            <Link to="/privacy-score" className="btn-primary btn-large">
              Начать защиту <FaArrowRight />
            </Link>
          </motion.div>

          {/* Stats */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.8, delay: 0.8 }}
            className="hero-stats"
          >
            <div className="stat-item">
              <div className="stat-value">48+</div>
              <div className="stat-label">Платформ для проверки</div>
            </div>
            <div className="stat-divider"></div>
            <div className="stat-item">
              <div className="stat-value">k-Anon</div>
              <div className="stat-label">Безопасная проверка</div>
            </div>
            <div className="stat-divider"></div>
            <div className="stat-item">
              <div className="stat-value">100%</div>
              <div className="stat-label">Локальная обработка</div>
            </div>
          </motion.div>
        </div>

        {/* Animated decorative elements */}
        <div className="hero-decoration">
          <div className="deco-circle deco-1"></div>
          <div className="deco-circle deco-2"></div>
          <div className="deco-circle deco-3"></div>
          <div className="deco-line deco-1"></div>
          <div className="deco-line deco-2"></div>
        </div>
      </section>

      {/* Features Grid */}
      <section className="features-section">
        <motion.h2
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true }}
          className="section-title"
        >
          ИНСТРУМЕНТЫ ЗАЩИТЫ
        </motion.h2>
        
        <motion.div
          variants={containerVariants}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true }}
          className="features-grid"
        >
          {features.map((feature, index) => (
            <motion.div
              key={index}
              variants={itemVariants}
              whileHover={{ y: -10, scale: 1.02 }}
              className="feature-card"
              style={{ '--card-color': feature.color }}
            >
              <Link to={feature.path} className="feature-link">
                <div className="feature-icon" style={{ color: feature.color }}>
                  {feature.icon}
                </div>
                <h3 className="feature-title">{feature.title}</h3>
                <p className="feature-description">{feature.description}</p>
                <div className="feature-arrow">
                  <FaArrowRight />
                </div>
              </Link>
            </motion.div>
          ))}
        </motion.div>
      </section>

      {/* Footer CTA */}
      <section className="footer-cta">
        <motion.div
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true }}
          className="footer-cta-content"
        >
          <h2>ВАША ПРИВАТНОСТЬ — ВАША СИЛА</h2>
          <p>Используйте мощь альтернативных личностей и фейковых данных для максимальной защиты</p>
        </motion.div>
      </section>
    </div>
  );
};

export default Homepage;
