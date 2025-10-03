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
      className={cn(
        "relative overflow-hidden rounded-2xl border border-white/10",
        // refined glass: deeper gradient, blur, subtle inner ring and shadow
        "bg-gradient-to-br from-blue-950 via-blue-900 to-blue-700 backdrop-blur-xl",
        "shadow-[0_0_0_1px_rgba(255,255,255,0.06),0_16px_40px_-12px_rgba(2,6,23,0.65)]",
        className,
      )}
      aria-label="Process timeline"
      role="region"
    >
      {/* subtle grid overlay */}
      <div
        aria-hidden="true"
        className="pointer-events-none absolute inset-0 opacity-15"
        style={{
          backgroundImage:
            "linear-gradient(to_right, rgba(255,255,255,0.08) 1px, transparent 1px), linear-gradient(to_bottom, rgba(255,255,255,0.08) 1px, transparent 1px)",
          backgroundSize: "48px 48px",
        }}
      />
      {/* gentle radial highlight */}
      <div
        aria-hidden="true"
        className="pointer-events-none absolute -top-24 -left-24 h-64 w-64 rounded-full bg-[radial-gradient(circle_at_center,rgba(255,255,255,0.12),transparent_60%)]"
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
                className="rounded-full bg-white/10 px-3 py-1 text-xs font-medium text-white/90 ring-1 ring-white/15"
              >
                {b}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* divider */}
      <div className="relative z-10 h-px w-full bg-white/10" />

      {/* timeline */}
      <div className="relative z-10 p-4 md:p-6">
        <div className="relative pl-5 md:pl-6">
          {/* vertical guide */}
          <div aria-hidden="true" className="absolute left-2.5 top-1 bottom-1 w-px bg-white/15 md:left-3" />
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
                    "bg-white/10 ring-1 ring-inset ring-white/15",
                    isCurrent && "bg-white/15 ring-white/25",
                    !isCurrent && "hover:bg-white/[0.14]",
                  )}
                >
                  {/* marker */}
                  <span className="absolute -left-3 top-4 md:-left-3.5" aria-hidden="true">
                    {isDone ? (
                      <CheckCircle2 className="h-5 w-5 text-blue-300 drop-shadow" />
                    ) : isCurrent ? (
                      <span className="relative grid h-5 w-5 place-items-center">
                        <CircleDot className="h-5 w-5 text-blue-300" />
                        <span className="absolute inline-block h-5 w-5 animate-ping rounded-full bg-blue-300/30" />
                      </span>
                    ) : (
                      <span className="block h-5 w-5 rounded-full border border-white/30 bg-white/5" />
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
