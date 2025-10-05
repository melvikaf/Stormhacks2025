import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import './App.css';
import { PerlinNoiseBackground } from './assets/PerlinNoise';

import BackButton from './assets/BackButton';
import Home from './pages/Home';
import About from './pages/About';
import Playlist from './pages/Playlist';
import DJ from "./pages/DJ";

function App() {
  return (
    <Router>
      <div>
        <PerlinNoiseBackground />
        <nav className="navbar">
          <BackButton />
          <div className="nav-container">
            <ul className="nav-links">
              <li><a href="/">Home</a></li>
              <li><a href="/about">About</a></li>
              <li><a href="/playlist">Playlist</a></li>
            </ul>
          </div>
        </nav>

        <Routes>
          <Route path="/" element={<Home />} />
          <Route path='/about' element={<About />} />
          <Route path="/playlist" element={<Playlist />} />
          <Route path="/playlist/:id" element={<DJ />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;