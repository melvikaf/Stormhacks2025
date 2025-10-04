import { useState } from 'react'
import './App.css'

function App() {
  const [count, setCount] = useState(0)

  return (
    <div>
      <nav className="navbar">
        <p>logo</p>
        <div className="nav-container">
          <ul className="nav-links">
            <li><a href="#">Home</a></li>
            <li><a href="#">About</a></li>
            <li><a href="#">Projects</a></li>
            <li><a href="#">Contact</a></li>
          </ul>
        </div>
      </nav>

      <h1>SHAKA</h1>

      <section class="button-nav">
        <a href='#'>ABOUT</a>
        <a href='#'>START</a>
      </section>
    </div>
  );
}

export default App;