import { useState, useEffect } from 'react';
import { useNavigate } from "react-router-dom";

function Playlist() {
  const [searchQuery, setSearchQuery] = useState('');
  const [playlists, setPlaylists] = useState([]);
  const [filteredPlaylists, setFilteredPlaylists] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  const mockPlaylists = [
    { id: 1, name: 'Chill Vibes', songs: ['Song One', 'Song Two', 'Song Three'] },
    { id: 2, name: 'Workout Mix', songs: ['Pump It Up', 'Energy Boost', 'Power Song'] },
    { id: 3, name: 'Focus Mode', songs: ['Concentration', 'Deep Work', 'Study Time'] },
    { id: 4, name: 'Road Trip', songs: ['Highway Tune', 'Open Road', 'Adventure Awaits'] }
  ];

  const handleSearch = (e) => {
    e.preventDefault();
    const query = searchQuery.toLowerCase();
    const results = playlists.filter((playlist) =>
      playlist.name.toLowerCase().includes(query)
    );
    setFilteredPlaylists(results);
  };

  const handlePlaylistClick = (playlist) => {
    navigate(`/playlist/${playlist.id}`, { state: { playlist } });
  };

  useEffect(() => {
    setLoading(true);
    const timer = setTimeout(() => {
      try {
        setPlaylists(mockPlaylists);
        setFilteredPlaylists(mockPlaylists);
        setLoading(false);
      } catch {
        setError('Failed to load playlists');
        setLoading(false);
      }
    }, 1000);
    return () => clearTimeout(timer);
  }, []);

  return (
    <div className="content">
      <div id="playlist">
        <h2>Choose your Playlist</h2>

        <div className="search-container">
          <form onSubmit={handleSearch}>
            <input
              type="text"
              className="search-bar"
              placeholder="Search playlists..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
          </form>
        </div>

        <div className="playlist-content">
          {loading && <p>Loading playlists...</p>}
          {error && <p>Error: {error}</p>}
          {!loading && !error && filteredPlaylists.length === 0 && (
            <p>No playlists found.</p>
          )}

          <ul className="playlist-grid">
            {filteredPlaylists.map((playlist) => (
              <li
                key={playlist.id}
                onClick={() => handlePlaylistClick(playlist)}
                className="playlist-item"
              >
                <strong className="playlist-title">{playlist.name}</strong>
                <div className="song-dropdown">
                  <ul>
                    {playlist.songs.map((song, idx) => (
                      <li key={idx} className="song-item">{song}</li>
                    ))}
                  </ul>
                </div>
              </li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  );
}

export default Playlist;
