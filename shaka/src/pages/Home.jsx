import { Link } from 'react-router-dom';

function Home() {
  return (
    <div className="content" id="home-title">  {/* Change class to className */}
      <h1>SHAKA</h1>
      <h3>Lorem ipsum dolor sit amet Lorem ipsum dolor sit amet Lorem ipsum dolor sit amet Lorem ipsum dolor sit amet Lorem ipsum dolor sit amet Lorem ipsum dolor sit amet </h3>
      
      <section className="button-nav">  {/* Change class to className */}
        <Link to="/about">ABOUT</Link>
        <Link to="/playlist">PLAYLIST</Link>
      </section>
    </div>
  );
}

export default Home;