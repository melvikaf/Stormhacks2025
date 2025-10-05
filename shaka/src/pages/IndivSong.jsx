import { useState } from 'react';

function IndivSong() {
  const [searchQuery, setSearchQuery] = useState('');

  const handleSearch = (e) => {
    e.preventDefault();
    console.log('Searching for:', searchQuery);
    // Add your playlist search logic here
  };

  return (
    <div className="content">
      <h2>Manage your Songs</h2>
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

      {/* Playlist */}
      <div class="playlist-content">
        <p>Select a playlist to see songs.</p>
      </div>
    </div>
  );
}

export default IndivSong;