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
        const scale = 0.001
        const timeScale = 0.004
        const gridSize = 15
        const maxRadius = 5

        const animate = () => {
            ctx.fillStyle = "#000"
            ctx.fillRect(0, 0, canvas.width, canvas.height)

            for (let y = 0; y < canvas.height; y += gridSize) {
                for (let x = 0; x < canvas.width; x += gridSize) {
                    const noise1 = perlin(x * scale, y * scale + time)
                    const noise2 = perlin(x * scale * 2, y * scale * 2 + time * 1.5)
                    const combinedNoise = (noise1 + noise2 * 0.5) / 1.1
                    const normalizedNoise = (combinedNoise + 1) / 2

                    const offsetX = Math.sin(time * 2 + x * 0.01) * 30
                    const offsetY = Math.cos(time * 2 + y * 0.01) * -20

                    const pulse = Math.sin(time * 3 + x * 0.02 + y * 0.02) * 0.3 + 0.7
                    const dx = x - mouseX
                    const dy = y - mouseY
                    const distance = Math.sqrt(dx * dx + dy * dy)
                    const maxDistance = 300

                    let proximityBoost = 1
                    if (distance < maxDistance) {
                        proximityBoost = 1 + (1 - distance / maxDistance) * 1.5 // up to 2.5× bigger
                    }
                    const radius = normalizedNoise * maxRadius * pulse / proximityBoost

                    const redValue = Math.floor(100 + 100 * Math.sin(x * 0.01 + time));
                    const greenValue = Math.floor(100 + 100 * Math.sin(y * 0.01 + time + 1));
                    const blueValue = Math.floor(100 + 100 * normalizedNoise);

                    ctx.beginPath()
                    ctx.arc(x + offsetX, y + offsetY, radius, 0, Math.PI * 2)
                    ctx.fillStyle = `rgb(${redValue}, ${greenValue}, ${blueValue})`
                    ctx.fill()
                }
            }

            time += timeScale
            requestAnimationFrame(animate)
        }

        let mouseX = -9999
        let mouseY = -9999

        const updateMousePosition = (e: MouseEvent) => {
            mouseX = e.clientX
            mouseY = e.clientY
        }

        window.addEventListener("mousemove", updateMousePosition)

        animate()

        return () => {
            window.removeEventListener("resize", setCanvasSize)
            window.removeEventListener("mousemove", updateMousePosition)
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
            zIndex: -1, 
        }}
        aria-hidden="true"
    />

}
