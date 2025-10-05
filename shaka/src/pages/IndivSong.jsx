import { Route, useLocation } from "react-router-dom";
import { Link } from 'react-router-dom';

function IndivSong() {
    const location = useLocation();
    const playlist = location.state?.playlist; // get playlist passed via state

    if (!playlist) {
        return <p>No playlist selected.</p>;
    }

    return (
        <div className="content">
            <h2>{playlist.name}</h2>
            <ul>
                {playlist.songs.map((song, idx) => (
                    <li key={idx}>{song}</li>
                ))}
            </ul>
            <section className="play-btn">
                <Link to="/dj" state={{ playlist }}>
                    START PLAYING
                </Link>
            </section>
        </div>
    );
}

export default IndivSong;
