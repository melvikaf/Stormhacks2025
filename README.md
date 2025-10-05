# Stormhacks2025

# 🎧 Shaka – Air DJ  

Shaka is an interactive Air DJ tool that transforms your webcam into a hands-free music controller.  
Using real-time gesture recognition, users can control music effects such as pitch, reverb, and crossfade — all through simple hand movements.  

---

##  Installation & Setup Guide  

Follow these steps to set up **Shaka – Air DJ** locally.

---

### 1. Frontend Setup (React + Vite)

```bash
npm create vite@latest frontend --template react
cd frontend
npm install
npm run dev

Dependencies:

core gesture + backend dependencies:
pip install mediapipe==0.10.14
pip install opencv-python
pip install numpy
pip install websockets
pip install aiohttp
pip install flask flask-cors

audio and signal librariries:
pip install sounddevice
pip install pydub
pip install requests
pip install mido
pip install python-rtmidi
