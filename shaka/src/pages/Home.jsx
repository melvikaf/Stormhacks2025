import { Link } from 'react-router-dom';

function Home() {
  return (
    <div className="content" id="home-title">  {/* Change class to className */}
      <h1>SHAKA</h1>
      <h3>Air DJ is a touchless DJ experience that lets you control and mix music using hand gestures. Wave, clap, or point to play, pause, and remix tracks in real time, turning your movements into a live performance.
      </h3>
      <section className="button-nav">  {/* Change class to className */}
        <Link to="/playlist">START CREATING</Link>
        <Link to="/about">ABOUT</Link>
      </section>
    </div>
  );
}

export default Home;