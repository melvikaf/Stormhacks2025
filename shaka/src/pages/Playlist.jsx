import { useState, useEffect } from 'react';

function Playlist() {
  const [searchQuery, setSearchQuery] = useState('');
  const [playlists, setPlaylists] = useState([]);
  const [filteredPlaylists, setFilteredPlaylists] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Mock data - replace with your actual data
  const mockPlaylists = [
    {
      id: 1,
      name: 'Chill Vibes',
      songs: ['Song One', 'Song Two', 'Song Three']
    },
    {
      id: 2,
      name: 'Workout Mix',
      songs: ['Pump It Up', 'Energy Boost', 'Power Song']
    },
    {
      id: 3,
      name: 'Focus Mode',
      songs: ['Concentration', 'Deep Work', 'Study Time']
    },
    {
      id: 4,
      name: 'Road Trip',
      songs: ['Highway Tune', 'Open Road', 'Adventure Awaits']
    }
  ];

  // Mock API call with setTimeout
  useEffect(() => {
    setLoading(true);
    
    const timer = setTimeout(() => {
      try {
        setPlaylists(mockPlaylists);
        setFilteredPlaylists(mockPlaylists);
        setLoading(false);
      } catch (err) {
        setError('Failed to load playlists');
        setLoading(false);
      }
    }, 1000); // Simulate network delay

    return () => clearTimeout(timer);
  }, []);

  const handleSearch = (e) => {
    e.preventDefault();
    const query = searchQuery.toLowerCase();
    const results = playlists.filter((playlist) =>
      playlist.name.toLowerCase().includes(query)
    );
    setFilteredPlaylists(results);
  };

  return (
    <div className="content">
      <h2>Choose your Playlist</h2>

      {/* Search Bar */}
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

      {/* Playlist Content */}
      <div className="playlist-content">
        {loading && <p>Loading playlists...</p>}
        {error && <p>Error: {error}</p>}
        {!loading && !error && filteredPlaylists.length === 0 && (
          <p>No playlists found.</p>
        )}
        
        <ul style={{ listStyle: 'none', padding: 0 }}>
          {filteredPlaylists.map((playlist) => (
            <li key={playlist.id} style={{ 
              marginBottom: '2rem', 
              padding: '1rem', 
              border: '2px solid #1F41DA',
              borderRadius: '8px'
            }}>
              <strong style={{ 
                fontSize: '2rem', 
                color: '#C44DEB',
                fontFamily: 'babapro'
              }}>{playlist.name}</strong>
              <ul style={{ marginTop: '1rem', paddingLeft: '1rem' }}>
                {playlist.songs.map((song, idx) => (
                  <li key={idx} style={{ 
                    color: 'white', 
                    fontSize: '1.2rem',
                    marginBottom: '0.5rem'
                  }}>
                    {song}
                  </li>
                ))}
              </ul>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}

export default Playlist;