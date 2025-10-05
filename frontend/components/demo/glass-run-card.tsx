import type * as React from "react"
import Link from "next/link"
import { cn } from "@/lib/utils"

type MiniStepStatus = "done" | "current" | "upcoming"

interface MiniStep {
  key: string
  status: MiniStepStatus
}

interface GlassRunCardProps {
  href: string
  dateLabel: string // e.g., "Sep 26"
  region: string // e.g., "India Main"
  company: string // e.g., "ACME India Ltd"
  totalAmount: string // e.g., "$243,500"
  status: string // e.g., "In Progress"
  steps: MiniStep[] // expected length 5
  className?: string
}

export function GlassRunCard({
  href,
  dateLabel,
  region,
  company,
  totalAmount,
  status,
  steps,
  className,
}: GlassRunCardProps) {
  return (
    <article
      className={cn(
        "relative overflow-hidden rounded-2xl border border-primary/20 bg-background/40 backdrop-blur-xl ring-1 ring-primary/10",
        "p-4 sm:p-5",
        className,
      )}
      // component-scoped gradient variables for a blue glass look
      style={
        {
          ["--glass-from" as any]: "215 92% 62%",
          ["--glass-to" as any]: "190 95% 44%",
        } as React.CSSProperties
      }
      aria-label="Payroll run summary"
      role="article"
    >
      {/* gradient washes */}
      <div
        className="pointer-events-none absolute inset-0"
        style={{
          background:
            "radial-gradient(110% 60% at 0% 0%, hsl(var(--glass-from)/0.18) 0%, transparent 60%), radial-gradient(120% 100% at 100% 100%, hsl(var(--glass-to)/0.22) 0%, transparent 55%)",
        }}
        aria-hidden="true"
      />
      {/* subtle grid overlay */}
      <div
        className="pointer-events-none absolute inset-0 opacity-20"
        style={{
          backgroundImage:
            "repeating-linear-gradient(to right, hsl(var(--foreground)/0.08) 0 1px, transparent 1px 24px), repeating-linear-gradient(to bottom, hsl(var(--foreground)/0.08) 0 1px, transparent 1px 24px)",
        }}
        aria-hidden="true"
      />

      <div className="relative z-10 grid grid-cols-1 md:grid-cols-12 gap-4">
        {/* Left: date + org */}
        <div className="md:col-span-4 flex items-center justify-between md:block">
          <div className="text-sm text-foreground/70">{dateLabel}</div>
          <div className="mt-1">
            <div className="text-base font-medium text-foreground text-pretty">{region}</div>
            <div className="text-sm text-foreground/70">{company}</div>
          </div>
        </div>

        {/* Middle: mini 5-step progress */}
        <div className="md:col-span-5 flex items-center">
          <ol className="flex w-full items-center justify-between gap-2" aria-label="Process steps">
            {steps.map((s, i) => (
              <li key={s.key} className="flex-1" aria-current={s.status === "current" ? "step" : undefined}>
                <div className="flex items-center">
                  <span
                    className={cn(
                      "h-2.5 w-2.5 rounded-full border",
                      s.status === "done"
                        ? "bg-primary border-primary"
                        : s.status === "current"
                          ? "bg-background border-primary"
                          : "bg-background border-border/60",
                    )}
                    aria-label={
                      s.status === "done"
                        ? `Step ${i + 1} complete`
                        : s.status === "current"
                          ? `Step ${i + 1} current`
                          : `Step ${i + 1} upcoming`
                    }
                  />
                  {i < steps.length - 1 && (
                    <div className={cn("mx-2 h-px flex-1", s.status === "done" ? "bg-primary/70" : "bg-border/70")} />
                  )}
                </div>
              </li>
            ))}
          </ol>
        </div>

        {/* Right: amount + status + link */}
        <div className="md:col-span-3 flex items-center justify-end md:justify-start md:flex-col md:items-end gap-2">
          <div className="text-right">
            <div className="text-xs text-foreground/70">Total Amount</div>
            <div className="text-lg font-semibold text-foreground">{totalAmount}</div>
          </div>
          <span className="inline-flex items-center rounded-full bg-primary/20 text-foreground text-xs px-2.5 py-1">
            {status}
          </span>
          <Link
            href={href}
            className="inline-flex items-center rounded-md border border-border/60 bg-background/60 px-3 py-1.5 text-sm text-foreground hover:border-primary/50 hover:bg-background/80 transition"
          >
            View
          </Link>
        </div>
      </div>
    </article>
  )
}

export default GlassRunCard
