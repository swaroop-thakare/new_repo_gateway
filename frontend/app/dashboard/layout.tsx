import type React from "react"
import { DashboardNav } from "@/components/dashboard/dashboard-nav"

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <div className="min-h-screen bg-slate-950">
      <DashboardNav />
      <main className="container mx-auto px-4 py-6">{children}</main>
    </div>
  )
}
