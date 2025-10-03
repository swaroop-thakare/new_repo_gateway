"use client"

import type { ReactNode } from "react"
import { useState } from "react"
import { DemoSidebar } from "@/components/demo/sidebar"
import { TopBar } from "@/components/demo/top-bar"
import { AgentDrawer } from "@/components/demo/agent-drawer"

export default function BookDemoLayout({ children }: { children: ReactNode }) {
  const [isDrawerOpen, setIsDrawerOpen] = useState(false)

  return (
    <div className="min-h-screen bg-[#0a0a0a] text-white">
      <DemoSidebar />
      <div className="ml-64">
        <TopBar />
        <main className="min-h-[calc(100vh-4rem)] p-6">{children}</main>
      </div>
      <AgentDrawer isOpen={isDrawerOpen} onClose={() => setIsDrawerOpen(false)} />
    </div>
  )
}
