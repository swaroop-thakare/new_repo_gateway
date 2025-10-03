"use client"

import type * as React from "react"

type Props = {
  icon: React.ReactNode
  title: string
  description: string
  time: string
}

export default function EventItem({ icon, title, description, time }: Props) {
  return (
    <div className="flex items-start justify-between gap-3 rounded-lg border border-white/10 bg-white/5 p-3">
      <div className="flex items-start gap-3">
        <div className="mt-0.5 flex size-6 items-center justify-center rounded-md bg-white/5">{icon}</div>
        <div className="space-y-0.5">
          <div className="text-sm font-medium text-white">{title}</div>
          <div className="text-xs text-gray-400">{description}</div>
        </div>
      </div>
      <div className="shrink-0 text-xs text-gray-400">{time}</div>
    </div>
  )
}
