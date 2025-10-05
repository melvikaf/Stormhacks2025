import { useLocation } from "react-router-dom";

function DJ() {
  const location = useLocation();
  const playlist = location.state?.playlist;

  return (
    <div className="content">
      {playlist ? (
        <>
          <p>Now playing: <strong>{playlist.name}</strong></p>
          <ul>
            {playlist.songs.map((song, idx) => (
              <li key={idx}>{song}</li>
            ))}
          </ul>
        </>
      ) : (
        <p>No playlist selected.</p>
      )}
    </div>
  );
}

export default DJ;
