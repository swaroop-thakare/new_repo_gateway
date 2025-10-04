"use client"

import { useState } from "react"
import { Header } from "@/components/header"
import { ThemeProvider } from "@/components/theme-provider"
import { MethodSelection } from "@/components/method-selection"
import { BatchUploadView } from "@/components/batch-upload-view"
import { StreamingView } from "@/components/streaming-view"

type View = "selection" | "batch" | "streaming"

export default function Home() {
  const [currentView, setCurrentView] = useState<View>("selection")

  return (
    <ThemeProvider defaultTheme="dark">
      <div className="min-h-screen bg-background">
        <Header />
        <main className="container mx-auto px-4 pt-24 pb-8">
          {currentView === "selection" && <MethodSelection onSelectMethod={setCurrentView} />}
          {currentView === "batch" && <BatchUploadView onBack={() => setCurrentView("selection")} />}
          {currentView === "streaming" && <StreamingView onBack={() => setCurrentView("selection")} />}
        </main>
      </div>
    </ThemeProvider>
  )
}
