# backend/jamendo_player.py
# Fetches 2 music playlists from Jamendo and plays random tracks
# Requires: pip install requests pydub simpleaudio zipfile36

import requests, random, threading, time, os, shutil, io, zipfile
from pydub import AudioSegment
from pydub.playback import _play_with_simpleaudio

# ------------------------------------------
# Config
# ------------------------------------------
CLIENT_ID = "b4cd9efe"
PLAYLISTS_URL = "https://api.jamendo.com/v3.0/playlists/"
DOWNLOAD_BASE = "https://storage.jamendo.com/download"

# ------------------------------------------
# FFmpeg setup
# ------------------------------------------
def ensure_ffmpeg():
    ffmpeg_path = shutil.which("ffmpeg")
    if not ffmpeg_path:
        possible_path = r"C:\ffmpeg\bin"
        if os.path.exists(possible_path):
            os.environ["PATH"] += os.pathsep + possible_path
            print("✅ Added C:\\ffmpeg\\bin to PATH and found ffmpeg.")
        else:
            print("⚠️ FFmpeg not found — please install to C:\\ffmpeg\\bin")
    else:
        print(f"✅ Using FFmpeg from: {ffmpeg_path}")

ensure_ffmpeg()

# ------------------------------------------
# Jamendo Player
# ------------------------------------------
class JamendoPlayer:
    def __init__(self):
        self.playlists = []
        self.tracks = []
        self.current = None
        self.thread = None
        self.stop_flag = False
        self._load_playlists()

    def _load_playlists(self):
        print("🎶 Fetching Jamendo playlists (limit=2)...")
        try:
            resp = requests.get(
                PLAYLISTS_URL,
                params={
                    "client_id": CLIENT_ID,
                    "format": "json",
                    "limit": 2,  # ✅ only 2 playlists now
                    "order": "creationdate_desc",
                },
                timeout=10,
            )
            print(f"HTTP status: {resp.status_code}")
            data = resp.json()
            print(f"Results count: {data['headers'].get('results_count', 0)}")

            self.playlists = data.get("results", [])
            if not self.playlists:
                print("⚠️ No playlists found — using Pixabay fallback.")
                self.tracks = [{
                    "name": "Sample Track",
                    "artist_name": "Pixabay Artist",
                    "audio": "https://cdn.pixabay.com/download/audio/2022/03/15/audio_8a1db7ef0a.mp3"
                }]
                return

            self._extract_tracks_from_zip()

        except Exception as e:
            print(f"❌ Jamendo playlist fetch failed: {e}")
            self.tracks = [{
                "name": "Sample Track",
                "artist_name": "Pixabay Artist",
                "audio": "https://cdn.pixabay.com/download/audio/2022/03/15/audio_8a1db7ef0a.mp3"
            }]

    def _extract_tracks_from_zip(self):
        print("📦 Downloading and extracting MP3s from playlists...")
        for p in self.playlists:
            zip_url = p.get("zip")
            if not zip_url:
                print(f"⚠️ Playlist {p.get('id')} has no zip link.")
                continue
            try:
                print(f"🔗 {zip_url}")
                r = requests.get(zip_url, timeout=10)
                if r.status_code != 200:
                    print(f"⚠️ Skipping {zip_url} (HTTP {r.status_code})")
                    continue

                # Extract the MP3s
                z = zipfile.ZipFile(io.BytesIO(r.content))
                count = 0
                for name in z.namelist():
                    if name.lower().endswith(".mp3"):
                        self.tracks.append({
                            "name": name,
                            "artist_name": p.get("user_name", "Unknown"),
                            "audio_data": z.read(name),
                        })
                        count += 1
                print(f"✅ Added {count} tracks from playlist '{p.get('name')}'")

            except Exception as e:
                print(f"⚠️ Could not process playlist: {e}")

        if not self.tracks:
            print("⚠️ No playable tracks — using fallback.")
            self.tracks = [{
                "name": "Sample Track",
                "artist_name": "Pixabay Artist",
                "audio": "https://cdn.pixabay.com/download/audio/2022/03/15/audio_8a1db7ef0a.mp3"
            }]

    def _play(self, audio_data, name):
        try:
            print(f"🎧 Playing: {name}")
            audio = AudioSegment.from_file(io.BytesIO(audio_data), format="mp3")

            def _thread():
                if self.stop_flag:
                    return
                play_obj = _play_with_simpleaudio(audio)
                play_obj.wait_done()

            self.thread = threading.Thread(target=_thread, daemon=True)
            self.thread.start()

        except Exception as e:
            print(f"❌ Playback error: {e}")

    def play_next(self):
        if not self.tracks:
            print("⚠️ No tracks loaded — reloading...")
            self._load_playlists()
            if not self.tracks:
                print("❌ Still no tracks.")
                return

        self.stop()
        self.current = random.choice(self.tracks)
        print(f"▶ Now playing: {self.current['name']} — {self.current['artist_name']}")
        self.stop_flag = False
        if "audio_data" in self.current:
            self._play(self.current["audio_data"], self.current["name"])
        else:
            r = requests.get(self.current["audio"], timeout=15)
            if r.status_code == 200:
                self._play(r.content, self.current["name"])
            else:
                print("⚠️ Fallback track unavailable.")

    def stop(self):
        self.stop_flag = True
        print("⏹️ Stopped playback (threaded audio will stop soon).")

    def resume(self):
        if self.current:
            print(f"▶ Restarting: {self.current['name']}")
            self.stop_flag = False
            if "audio_data" in self.current:
                self._play(self.current["audio_data"], self.current["name"])
            else:
                r = requests.get(self.current["audio"], timeout=15)
                if r.status_code == 200:
                    self._play(r.content, self.current["name"])
        else:
            self.play_next()


if __name__ == "__main__":
    player = JamendoPlayer()
    time.sleep(1)
    player.play_next()
    time.sleep(20)
    player.stop()
