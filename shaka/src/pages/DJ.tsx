"use client"

import { useState, useEffect, useRef } from "react"
import { useLocation } from "react-router-dom"

interface Playlist {
  name: string
  songs: string[]
}

export default function DJ() {
  const location = useLocation()
  const playlist = location.state?.playlist as Playlist | undefined
  const [currentIndex, setCurrentIndex] = useState(0)
  const [isPlaying, setIsPlaying] = useState(false)
  const [progress, setProgress] = useState(0)
  const [lastGesture, setLastGesture] = useState("None")

  // ✅ TypeScript-friendly refs
  const audioRef = useRef<HTMLAudioElement>(null)
  const imgRef = useRef<HTMLImageElement>(null)

  if (!playlist) {
    return <p className="p-6 text-center text-gray-600">No playlist selected.</p>
  }

  const currentSong = {
    title: playlist.songs[currentIndex],
    url: `/songs/${playlist.songs[currentIndex]}.mp3`,
  }

  const nextSong = playlist.songs[currentIndex + 1]

  // ---------------------------
  // WebSocket connection (gestures)
  // ---------------------------
  useEffect(() => {
    const socket = new WebSocket("ws://localhost:8765")

    socket.onopen = () => console.log("✅ Connected to gesture WebSocket")

    socket.onmessage = (event) => {
      const msg = JSON.parse(event.data)

      if (msg.type === "gesture") {
        setLastGesture(msg.name)
      }

      if (msg.type === "action") {
        if (msg.name === "play") {
          audioRef.current?.play()
          setIsPlaying(true)
        }
        if (msg.name === "pause") {
          audioRef.current?.pause()
          setIsPlaying(false)
        }
        if (msg.name === "next_track") {
          setCurrentIndex((i) =>
            Math.min(i + 1, playlist.songs.length - 1)
          )
          setIsPlaying(true)
        }
        if (msg.name === "previous_track") {
          setCurrentIndex((i) => Math.max(i - 1, 0))
          setIsPlaying(true)
        }
      }
    }

    socket.onerror = (err) => console.error("WebSocket error:", err)

    return () => socket.close()
  }, [playlist])

  // ---------------------------
  // Manual play/pause toggle
  // ---------------------------
  const togglePlay = () => {
    const audio = audioRef.current
    if (!audio) return

    if (isPlaying) {
      audio.pause()
    } else {
      audio.play()
    }
    setIsPlaying(!isPlaying)
  }

  // ---------------------------
  // Progress bar tracking
  // ---------------------------
  useEffect(() => {
    const audio = audioRef.current
    if (!audio) return

    const updateProgress = () => {
      setProgress(audio.currentTime / (audio.duration || 1))
    }

    const handleEnded = () => {
      if (currentIndex < playlist.songs.length - 1) {
        setCurrentIndex(currentIndex + 1)
        setIsPlaying(true)
      } else {
        setIsPlaying(false)
      }
    }

    // ✅ Type-safe event listeners
    audio.addEventListener("timeupdate", updateProgress)
    audio.addEventListener("ended", handleEnded)

    return () => {
      audio.removeEventListener("timeupdate", updateProgress)
      audio.removeEventListener("ended", handleEnded)
    }
  }, [currentIndex, playlist.songs])

  // reload audio when song changes
  useEffect(() => {
    const audio = audioRef.current
    if (!audio) return
    audio.load()
    if (isPlaying) audio.play()
  }, [currentIndex, isPlaying])

  return (
    <div className="content flex flex-col items-center p-6 space-y-6">
      <h2 className="text-2xl font-bold mb-2" id="dj-title">Now Playing: {playlist.name}</h2>
      
      {/* ✅ Current / Next Songs + Play Control */}
      <div className="curr-next-songs">
  <div className="current-song">
    <span>Current:</span>
    <span>{currentSong.title}</span>
  </div>

  <div className="play-btn">
    <button onClick={togglePlay}>
      {isPlaying ? "⏸" : "▶"}
    </button>
  </div>

  {nextSong && (
    <div className="next-song">
      <span>Next:</span>
      <span>{nextSong}</span>
    </div>
  )}
</div>



      {/* ✅ Progress Bar */}
      <div className="w-[640px] h-2 bg-gray-300 rounded">
        <div
          className="h-2 bg-blue-500 rounded transition-all duration-150"
          style={{ width: `${progress * 100}%` }}
        />
      </div>

      {/* ✅ Hidden Audio Player */}
      <audio ref={audioRef}>
        <source src={currentSong.url} type="audio/mp3" />
      </audio>

      {/* ✅ Embedded gesture video feed from Python */}
      <div className="relative w-full max-w-3xl aspect-video border-4 border-blue-500 rounded-lg overflow-hidden shadow-lg">
  <img
    ref={imgRef}
    src="http://localhost:5000/video_feed"
    alt="Gesture feed"
    className="w-full h-full object-cover"
  />
</div>


          </div>
  )
}
