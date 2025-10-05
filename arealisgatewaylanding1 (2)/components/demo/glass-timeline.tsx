"use client"

import { cn } from "@/lib/utils"
import { CheckCircle2, CircleDot } from "lucide-react"

export type GlassStep = {
  label: string
  status: "done" | "current" | "pending"
  date?: string
}

export function GlassTimeline({
  steps,
  className,
  title,
  subtitle,
  person,
  badges, // new
}: {
  steps: GlassStep[]
  className?: string
  title?: string
  subtitle?: string
  person?: { name: string; amount: string; currency?: string; status?: string; avatarUrl?: string }
  badges?: string[] // new
}) {
  return (
    <div
      className={cn("relative overflow-hidden rounded-2xl border", "glass-card glass-primary", className)}
      aria-label="Process timeline"
      role="region"
    >
      {/* subtle grid overlay */}
      <div
        aria-hidden="true"
        className="pointer-events-none absolute inset-0 opacity-20"
        style={{
          backgroundImage:
            "repeating-linear-gradient(to right, color-mix(in oklab, var(--color-foreground) 8%, transparent) 0 1px, transparent 1px 24px), repeating-linear-gradient(to bottom, color-mix(in oklab, var(--color-foreground) 8%, transparent) 0 1px, transparent 1px 24px)",
        }}
      />
      {/* gentle radial highlight */}
      <div
        aria-hidden="true"
        className="pointer-events-none absolute -top-24 -left-24 h-64 w-64 rounded-full"
        style={{
          background:
            "radial-gradient(circle at center, color-mix(in oklab, var(--color-foreground) 12%, transparent) 0%, transparent 60%)",
        }}
      />
      {/* top header */}
      {(title || subtitle || person) && (
        <div className="relative z-10 grid grid-cols-1 gap-4 p-6 md:grid-cols-[auto_1fr] md:items-center">
          {person ? (
            <div className="flex items-center gap-4">
              <img
                src={person.avatarUrl || "/placeholder.svg?height=64&width=64&query=person-avatar"}
                alt={`Avatar for ${person.name}`}
                className="h-16 w-16 rounded-xl object-cover ring-1 ring-white/20"
                crossOrigin="anonymous"
              />
              <div className="min-w-0">
                {/* frequency chip */}
                {subtitle ? (
                  <span className="mb-1 inline-flex items-center rounded-full bg-white/10 px-2.5 py-0.5 text-xs font-medium text-white/85 ring-1 ring-white/15">
                    {subtitle}
                  </span>
                ) : null}
                <div className="text-pretty text-2xl font-semibold leading-snug">{person.name}</div>
                <div className="mt-1 flex flex-wrap items-baseline gap-2">
                  <div className="text-3xl font-bold leading-none tracking-tight">{person.amount}</div>
                  {person.currency ? <span className="text-sm text-white/80">{person.currency}</span> : null}
                  {person.status ? (
                    <span className="ml-1 inline-flex items-center gap-1 rounded-full bg-white/10 px-2 py-0.5 text-xs font-medium text-white/90 ring-1 ring-white/15">
                      <span className="inline-block h-2 w-2 rounded-full bg-white/70" />
                      {person.status}
                    </span>
                  ) : null}
                </div>
              </div>
            </div>
          ) : (
            <div>
              {subtitle ? (
                <span className="mb-1 inline-flex items-center rounded-full bg-white/10 px-2.5 py-0.5 text-xs font-medium text-white/85 ring-1 ring-white/15">
                  {subtitle}
                </span>
              ) : null}
              {title ? <h3 className="text-2xl font-semibold">{title}</h3> : null}
            </div>
          )}

          {/* right-side chips */}
          <div className="flex flex-wrap items-center gap-2 md:justify-end">
            {(badges && badges.length ? badges : ["Needs Approval", "Payroll"]).map((b) => (
              <span
                key={b}
                className="rounded-full bg-foreground/10 px-3 py-1 text-xs font-medium text-foreground/90 ring-1 ring-foreground/15"
              >
                {b}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* divider */}
      <div className="relative z-10 h-px w-full bg-foreground/10" />

      {/* timeline */}
      <div className="relative z-10 p-4 md:p-6">
        <div className="relative pl-5 md:pl-6">
          {/* vertical guide */}
          <div aria-hidden="true" className="absolute left-2.5 top-1 bottom-1 w-px bg-foreground/15 md:left-3" />
          <ol role="list" className="space-y-3">
            {steps.map((s, idx) => {
              const isDone = s.status === "done"
              const isCurrent = s.status === "current"
              return (
                <li
                  key={s.label + idx}
                  role="listitem"
                  className={cn(
                    "relative rounded-xl p-4 md:p-5 transition-colors",
                    "bg-foreground/[0.06] ring-1 ring-inset ring-foreground/15",
                    isCurrent && "bg-foreground/[0.10] ring-foreground/25",
                    !isCurrent && "hover:bg-foreground/[0.09]",
                  )}
                >
                  <span className="absolute -left-3 top-4 md:-left-3.5" aria-hidden="true">
                    {isDone ? (
                      <CheckCircle2 className="h-5 w-5 text-primary drop-shadow" />
                    ) : isCurrent ? (
                      <span className="relative grid h-5 w-5 place-items-center">
                        <CircleDot className="h-5 w-5 text-primary" />
                        <span className="absolute inline-block h-5 w-5 animate-ping rounded-full bg-primary/30" />
                      </span>
                    ) : (
                      <span className="block h-5 w-5 rounded-full border border-foreground/30 bg-background/50" />
                    )}
                  </span>

                  <div className="flex items-center justify-between gap-3">
                    <p
                      className={cn(
                        "text-sm md:text-base font-medium",
                        isDone && "text-white",
                        isCurrent && "text-white",
                        !isDone && !isCurrent && "text-white/85",
                      )}
                    >
                      {s.label}
                    </p>
                    {s.date ? <span className="text-xs text-white/70">{s.date}</span> : null}
                  </div>
                </li>
              )
            })}
          </ol>
        </div>
      </div>
    </div>
  )
}
