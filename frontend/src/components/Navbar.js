import React, { useState, useEffect } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  FaShieldAlt, 
  FaSearch, 
  FaUserSecret, 
  FaKey, 
  FaImage, 
  FaDatabase, 
  FaChartLine,
  FaBars,
  FaTimes,
  FaHome,
  FaRobot
} from 'react-icons/fa';
import './Navbar.css';

const Navbar = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [scrolled, setScrolled] = useState(false);
  const location = useLocation();

  useEffect(() => {
    const handleScroll = () => {
      setScrolled(window.scrollY > 20);
    };
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  useEffect(() => {
    setIsOpen(false);
  }, [location]);

  const navItems = [
    { path: '/', label: 'Главная', icon: <FaHome /> },
    { path: '/email-check', label: 'Email Check', icon: <FaSearch /> },
    { path: '/username-check', label: 'Username OSINT', icon: <FaUserSecret /> },
    { path: '/password-check', label: 'Password Check', icon: <FaKey /> },
    { path: '/exif-cleaner', label: 'EXIF Cleaner', icon: <FaImage /> },
    { path: '/fake-generator', label: 'Fake Generator', icon: <FaRobot /> },
    { path: '/identities', label: 'Identities', icon: <FaDatabase /> },
    { path: '/privacy-score', label: 'Privacy Score', icon: <FaChartLine /> },
  ];

  return (
    <motion.nav 
      className={`navbar ${scrolled ? 'scrolled' : ''}`}
      initial={{ y: -100 }}
      animate={{ y: 0 }}
      transition={{ duration: 0.5 }}
    >
      <div className="navbar-container">
        <Link to="/" className="navbar-logo">
          <motion.div
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            <FaShieldAlt className="logo-icon" />
            <span className="logo-text">
              <span className="glitch" data-text="ANTI-OSINT">ANTI-OSINT</span>
            </span>
          </motion.div>
        </Link>

        {/* Desktop Menu */}
        <div className="desktop-menu">
          {navItems.map((item) => (
            <Link
              key={item.path}
              to={item.path}
              className={`nav-link ${location.pathname === item.path ? 'active' : ''}`}
            >
              <span className="nav-icon">{item.icon}</span>
              <span className="nav-label">{item.label}</span>
            </Link>
          ))}
        </div>

        {/* Mobile Menu Button */}
        <button 
          className="mobile-menu-btn"
          onClick={() => setIsOpen(!isOpen)}
        >
          {isOpen ? <FaTimes /> : <FaBars />}
        </button>
      </div>

      {/* Mobile Menu */}
      <AnimatePresence>
        {isOpen && (
          <motion.div
            className="mobile-menu"
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            transition={{ duration: 0.3 }}
          >
            {navItems.map((item) => (
              <Link
                key={item.path}
                to={item.path}
                className={`mobile-nav-link ${location.pathname === item.path ? 'active' : ''}`}
              >
                <span className="nav-icon">{item.icon}</span>
                <span className="nav-label">{item.label}</span>
              </Link>
            ))}
          </motion.div>
        )}
      </AnimatePresence>
    </motion.nav>
  );
};

export default Navbar;
