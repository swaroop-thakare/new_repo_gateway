"use client"

import type { ReactNode } from "react"
import { useState } from "react"
import { DemoSidebar } from "@/components/demo/sidebar"
import { TopBar } from "@/components/demo/top-bar"
import { AgentDrawer } from "@/components/demo/agent-drawer"
import { DemoFooter } from "@/components/demo/footer"

export default function BookDemoLayout({ children }: { children: ReactNode }) {
  const [isDrawerOpen, setIsDrawerOpen] = useState(false)

  return (
    <div className="min-h-screen bg-[#0a0a0a] text-white flex flex-col">
      <DemoSidebar />
      <div className="ml-64 flex flex-col flex-1">
        <TopBar />
        <main className="flex-1 p-6">{children}</main>
        <DemoFooter />
      </div>
      <AgentDrawer isOpen={isDrawerOpen} onClose={() => setIsDrawerOpen(false)} />
    </div>
  )
}
