import type React from "react"
import { cn } from "@/lib/utils"

type PageHeaderProps = {
  eyebrow?: string
  title: string
  description?: string
  actions?: React.ReactNode
  className?: string
}

// Simple, premium header with optional actions
export function PageHeader({ eyebrow, title, description, actions, className }: PageHeaderProps) {
  return (
    <header
      aria-labelledby="page-header-title"
      className={cn(
        // container: rounded, bordered, gradient overlay, glass
        "relative overflow-hidden rounded-xl border bg-gradient-to-r from-sky-500/30 via-blue-500/20 to-cyan-500/30",
        "supports-[backdrop-filter]:backdrop-blur shadow-sm ring-1 ring-border/60",
        "[box-shadow:inset_0_1px_0_rgba(255,255,255,0.08)]",
        className,
      )}
    >
      <div
        aria-hidden="true"
        className="pointer-events-none absolute -top-20 -right-28 h-64 w-64 rounded-full
                   bg-[radial-gradient(closest-side,rgba(0,0,0,0)_0%,rgba(0,0,0,0)_40%,transparent_60%)]
                   "
      />
      <div
        aria-hidden="true"
        className="pointer-events-none absolute -top-16 -right-24 h-56 w-56 rounded-full
                   bg-[radial-gradient(closest-side,color-mix(in_oklch,var(--color-primary)_35%,transparent),transparent_60%)]
                   blur-2xl"
      />
      <div
        aria-hidden="true"
        className="pointer-events-none absolute -bottom-10 -left-16 h-40 w-40 rounded-full
                   bg-[radial-gradient(closest-side,color-mix(in_oklch,var(--color-primary)_20%,transparent),transparent_65%)]
                   blur-[6px]"
      />
      <div className="pointer-events-none absolute inset-x-0 top-0 h-px bg-primary/20" aria-hidden="true" />
      <div className="relative p-5 md:p-7">
        {eyebrow ? (
          <p className="mb-2 inline-flex items-center rounded-full bg-background/60 px-2 py-1 text-[10px] uppercase tracking-wide text-muted-foreground ring-1 ring-border/60">
            {eyebrow}
          </p>
        ) : null}
        <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
          <div>
            <h1 id="page-header-title" className="text-pretty text-2xl md:text-3xl font-semibold">
              {title}
            </h1>
            {description ? <p className="mt-1 text-sm text-muted-foreground">{description}</p> : null}
          </div>
          {actions ? <div className="flex items-center gap-2">{actions}</div> : null}
        </div>
      </div>
    </header>
  )
}
