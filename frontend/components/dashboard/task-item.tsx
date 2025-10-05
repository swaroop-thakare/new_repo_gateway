"use client"
import { cn } from "@/lib/utils"

type Priority = "high" | "medium" | "low"

type Props = {
  title: string
  description: string
  priority: Priority
  time: string
}

const priorityColor: Record<Priority, string> = {
  high: "bg-red-500",
  medium: "bg-yellow-500",
  low: "bg-blue-500",
}

export default function TaskItem({ title, description, priority, time }: Props) {
  return (
    <div className="flex items-start justify-between gap-3 rounded-lg border border-white/10 bg-white/5 p-3">
      <div className="flex items-start gap-3">
        <span className={cn("mt-1 inline-block size-2 rounded-full", priorityColor[priority])} aria-hidden="true" />
        <div className="space-y-0.5">
          <div className="text-sm font-medium text-white">{title}</div>
          <div className="text-xs text-gray-400">{description}</div>
        </div>
      </div>
      <div className="shrink-0 text-xs text-gray-400">{time}</div>
    </div>
  )
}
