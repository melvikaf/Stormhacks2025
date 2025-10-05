"use client"

import { useState, useEffect, useRef } from "react"
import { useLocation } from "react-router-dom"

interface Song {
  title: string
}

export default function DJ() {
  const location = useLocation()
  const playlist = location.state?.playlist
  const [currentIndex, setCurrentIndex] = useState(0)
  const [isPlaying, setIsPlaying] = useState(false)
  const [progress, setProgress] = useState(0)
  const audioRef = useRef<HTMLAudioElement | null>(null)

  if (!playlist) {
    return <p>No playlist selected.</p>
  }

  const currentSong = { title: playlist.songs[currentIndex], url: `/songs/${playlist.songs[currentIndex]}.mp3` }
  const nextSong = playlist.songs[currentIndex + 1]

  const togglePlay = () => {
    if (!audioRef.current) return
    if (isPlaying) {
      audioRef.current.pause()
    } else {
      audioRef.current.play()
    }
    setIsPlaying(!isPlaying)
  }

  useEffect(() => {
    const audio = audioRef.current
    if (!audio) return

    const updateProgress = () => {
      setProgress(audio.currentTime / (audio.duration || 1))
    }

    audio.addEventListener("timeupdate", updateProgress)
    audio.addEventListener("ended", () => {
      if (currentIndex < playlist.songs.length - 1) {
        setCurrentIndex(currentIndex + 1)
        setIsPlaying(true)
      } else {
        setIsPlaying(false)
      }
    })

    return () => {
      audio.removeEventListener("timeupdate", updateProgress)
    }
  }, [currentIndex, playlist.songs])

  useEffect(() => {
    if (!audioRef.current) return
    audioRef.current.load()
    if (isPlaying) audioRef.current.play()
  }, [currentIndex, isPlaying])

  return (
    <div className="content space-y-6">
      <h2 className="text-2xl font-bold">Now Playing: {playlist.name}</h2>

      <div className="curr-next-songs">
        <div className="current-song">
          <span>Current:</span>
          <span>{currentSong.title}</span>
        </div>

        {nextSong && (
          <div className="next-song">
            <span>Next:</span>
            <span>{nextSong}</span>
          </div>
        )}
      </div>

      <div className="progress-container">
        <div
          className="progress-bar"
          style={{ width: `${progress * 100}%` }}
        />
      </div>

      <div className="play-btn">
        <button onClick={togglePlay}>
          {isPlaying ? "⏸ Pause" : "▶️ Play"}
        </button>
      </div>
    </div>
  )
}
