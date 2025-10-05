import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { useState } from 'react';
import './App.css';
import BackButton from './assets/BackButton';
import Home from './pages/Home';
import Playlist from './pages/Playlist';

function App() {
  return (
    <Router>
      <div>
        <nav className="navbar">
          <BackButton />
          <div className="nav-container">
            <ul className="nav-links">
              <li><a href="/">Home</a></li>
              <li><a href="/about">About</a></li>
              <li><a href="/projects">Projects</a></li>
              <li><a href="/contact">Contact</a></li>
            </ul>
          </div>
        </nav>

        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/playlist" element={<Playlist />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;