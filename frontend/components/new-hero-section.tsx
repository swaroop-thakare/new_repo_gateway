"use client"

import { Button } from "@/components/ui/button"
import Link from "next/link"
import { Play, Pause } from "lucide-react"
import { useState, useRef } from "react"

export function NewHeroSection() {
  const [isPlaying, setIsPlaying] = useState(false)
  const videoRef = useRef<HTMLVideoElement>(null)

  const togglePlay = () => {
    if (videoRef.current) {
      if (isPlaying) {
        videoRef.current.pause()
      } else {
        videoRef.current.play()
      }
      setIsPlaying(!isPlaying)
    }
  }

  return (
    <section className="relative overflow-hidden bg-gradient-to-br from-background via-primary/5 to-accent/5">
      <div className="absolute inset-0 bg-[linear-gradient(to_right,#8080800a_1px,transparent_1px),linear-gradient(to_bottom,#8080800a_1px,transparent_1px)] bg-[size:24px_24px]" />

      <div className="container relative px-4 py-20 md:py-28 md:px-6">
        <div className="grid gap-12 lg:grid-cols-2 lg:gap-16 items-center">
          <div className="space-y-8">
            <h1 className="text-4xl font-bold tracking-tight sm:text-5xl md:text-6xl lg:text-7xl text-balance leading-[1.1]">
              The Smartest Way to <span className="text-primary">Move Money at Scale.</span>
            </h1>

            <p className="text-lg text-muted-foreground max-w-2xl text-pretty leading-relaxed">
              Arealis Magnus is a non-custodial financial intelligence layer that sits on top of banking rails (NEFT,
              RTGS, IMPS, UPI, NACH). We don't hold your funds — instead, we power faster disbursements, autonomous
              compliance, and real-time reconciliation. Think of it as the brains for your financial flows.
            </p>

            <div className="flex flex-wrap gap-4">
              <Button size="lg" className="font-semibold shadow-lg shadow-primary/25" asChild>
                <Link href="/book-demo">Request a Demo</Link>
              </Button>
              <Button size="lg" variant="outline" className="font-semibold bg-transparent" asChild>
                <Link href="/contact">Talk to Sales</Link>
              </Button>
            </div>
          </div>

          <div className="relative flex items-center justify-center">
            <div className="relative w-full max-w-2xl">
              <div className="relative aspect-video rounded-2xl border-2 border-border bg-card shadow-2xl overflow-hidden group">
                {/* Video element */}
                <video
                  ref={videoRef}
                  className="w-full h-full object-cover"
                  poster="/fintech-dashboard.png"
                  onPlay={() => setIsPlaying(true)}
                  onPause={() => setIsPlaying(false)}
                  onEnded={() => setIsPlaying(false)}
                >
                  <source src="/demo-video.mov" type="video/mp4" />
                  <source src="/demo-video.mov" type="video/quicktime" />
                  Your browser does not support the video tag.
                </video>

                {/* Play/Pause button overlay */}
                <div className="absolute inset-0 flex items-center justify-center">
                  <button 
                    onClick={togglePlay}
                    className="relative z-10 h-20 w-20 rounded-full bg-primary/90 backdrop-blur-sm flex items-center justify-center shadow-xl hover:scale-110 transition-transform group-hover:bg-primary"
                  >
                    {isPlaying ? (
                      <Pause className="h-8 w-8 text-primary-foreground" fill="currentColor" />
                    ) : (
                      <Play className="h-8 w-8 text-primary-foreground ml-1" fill="currentColor" />
                    )}
                  </button>
                </div>

                {/* Decorative elements */}
                <div className="absolute top-4 left-4 px-3 py-1.5 rounded-full bg-background/80 backdrop-blur-sm border text-xs font-medium">
                  Watch Demo
                </div>
                <div className="absolute bottom-4 right-4 px-3 py-1.5 rounded-full bg-background/80 backdrop-blur-sm border text-xs font-medium">
                  2:30
                </div>
              </div>

              {/* Floating stats cards */}
              <div className="absolute -bottom-6 -left-6 px-4 py-3 rounded-xl bg-card border-2 shadow-lg hidden lg:block">
                <div className="text-2xl font-bold text-primary">99.9%</div>
                <div className="text-xs text-muted-foreground">Uptime</div>
              </div>
              <div className="absolute -top-6 -right-6 px-4 py-3 rounded-xl bg-card border-2 shadow-lg hidden lg:block">
                <div className="text-2xl font-bold text-accent">₹10B+</div>
                <div className="text-xs text-muted-foreground">Processed</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}
