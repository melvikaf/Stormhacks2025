"use client"

import { useEffect, useRef } from "react"

export function PerlinNoiseBackground() {
    const canvasRef = useRef<HTMLCanvasElement>(null)

    useEffect(() => {
        const canvas = canvasRef.current
        if (!canvas) return

        const ctx = canvas.getContext("2d")
        if (!ctx) return

        // Set canvas size
        const setCanvasSize = () => {
            canvas.width = window.innerWidth
            canvas.height = window.innerHeight
        }
        setCanvasSize()
        window.addEventListener("resize", setCanvasSize)

        // Perlin noise implementation
        const permutation = new Array(256)
        for (let i = 0; i < 256; i++) {
            permutation[i] = i
        }
        // Shuffle
        for (let i = 255; i > 0; i--) {
            const j = Math.floor(Math.random() * (i + 1))
                ;[permutation[i], permutation[j]] = [permutation[j], permutation[i]]
        }
        const p = [...permutation, ...permutation]

        const fade = (t: number) => t * t * t * (t * (t * 6 - 15) + 10)
        const lerp = (t: number, a: number, b: number) => a + t * (b - a)
        const grad = (hash: number, x: number, y: number) => {
            const h = hash & 3
            const u = h < 2 ? x : y
            const v = h < 2 ? y : x
            return ((h & 1) === 0 ? u : -u) + ((h & 2) === 0 ? v : -v)
        }

        const perlin = (x: number, y: number) => {
            const X = Math.floor(x) & 255
            const Y = Math.floor(y) & 255
            x -= Math.floor(x)
            y -= Math.floor(y)
            const u = fade(x)
            const v = fade(y)
            const a = p[X] + Y
            const b = p[X + 1] + Y
            return lerp(
                v,
                lerp(u, grad(p[a], x, y), grad(p[b], x - 1, y)),
                lerp(u, grad(p[a + 1], x, y - 1), grad(p[b + 1], x - 1, y - 1)),
            )
        }

        let time = 0
        const scale = 0.002
        const timeScale = 0.002 // Faster animation
        const gridSize = 30
        const maxRadius = 10

        const animate = () => {
            ctx.fillStyle = "#000"
            ctx.fillRect(0, 0, canvas.width, canvas.height)

            for (let y = 0; y < canvas.height; y += gridSize) {
                for (let x = 0; x < canvas.width; x += gridSize) {
                    const noise1 = perlin(x * scale, y * scale + time)
                    const noise2 = perlin(x * scale * 2, y * scale * 2 + time * 1.5)
                    const combinedNoise = (noise1 + noise2 * 0.5) / 1.5
                    const normalizedNoise = (combinedNoise + 1) / 2

                    const offsetX = Math.sin(time * 2 + x * 0.01) * 5
                    const offsetY = Math.cos(time * 2 + y * 0.01) * 5

                    const pulse = Math.sin(time * 3 + x * 0.02 + y * 0.02) * 0.3 + 0.7
                    const radius = normalizedNoise * maxRadius * pulse

                    const opacity = normalizedNoise * 0.6 + 0.2
                    const blueValue = Math.floor(normalizedNoise * 100 + 155)

                    ctx.beginPath()
                    ctx.arc(x + offsetX, y + offsetY, radius, 0, Math.PI * 2)
                    ctx.fillStyle = `rgba(100, 120, ${blueValue}, ${opacity})`
                    ctx.fill()
                }
            }

            time += timeScale
            requestAnimationFrame(animate)
        }

        animate()

        return () => {
            window.removeEventListener("resize", setCanvasSize)
        }
    }, [])

    return <canvas
        ref={canvasRef}
        style={{
            position: "fixed",
            top: 0,
            left: 0,
            width: "100vw",
            height: "100vh",
            zIndex: -1, // behind everything
        }}
        aria-hidden="true"
    />

}
