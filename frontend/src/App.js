import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Navbar from './components/Navbar';
import MatrixBackground from './components/MatrixBackground';
import Homepage from './pages/Homepage';
import EmailCheck from './pages/EmailCheck';
import UsernameCheck from './pages/UsernameCheck';
import PasswordCheck from './pages/PasswordCheck';
import ExifCleaner from './pages/ExifCleaner';
import FakeGenerator from './pages/FakeGenerator';
import Identities from './pages/Identities';
import PrivacyScore from './pages/PrivacyScore';
import './App.css';

function App() {
  return (
    <Router>
      <div className="App">
        <MatrixBackground />
        <div className="bg-grid" />
        <div className="bg-orbs">
          <div className="bg-orb" />
          <div className="bg-orb" />
          <div className="bg-orb" />
        </div>
        <div className="scan-line" />
        
        <Navbar />
        
        <main className="main-content">
          <Routes>
            <Route path="/" element={<Homepage />} />
            <Route path="/email-check" element={<EmailCheck />} />
            <Route path="/username-check" element={<UsernameCheck />} />
            <Route path="/password-check" element={<PasswordCheck />} />
            <Route path="/exif-cleaner" element={<ExifCleaner />} />
            <Route path="/fake-generator" element={<FakeGenerator />} />
            <Route path="/identities" element={<Identities />} />
            <Route path="/privacy-score" element={<PrivacyScore />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;
