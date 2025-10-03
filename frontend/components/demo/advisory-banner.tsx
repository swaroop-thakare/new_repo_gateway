"use client"

import { TriangleAlert } from "lucide-react"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { Badge } from "@/components/ui/badge"

type AdvisoryBannerProps = {
  degradedRail?: string
  preferredRail?: string
  windowLabel?: string
  reason?: string
  className?: string
}

export function AdvisoryBanner({
  degradedRail = "NEFT",
  preferredRail = "IMPS",
  windowLabel = "30m",
  reason = "penalty high, window closing",
  className,
}: AdvisoryBannerProps) {
  return (
    <Alert
      className={`glass-card glass-warning text-warning-foreground ring-1 ring-warning/45 border-warning/30 ${className || ""}`}
      role="status"
      aria-live="polite"
    >
      <TriangleAlert className="h-4 w-4" />
      <AlertDescription className="text-sm">
        <div className="flex flex-wrap items-center gap-2">
          <span className="font-medium text-warning-foreground/95">Advisories:</span>
          <Badge
            variant="outline"
            className="px-2.5 py-0.5 text-xs bg-warning/25 text-warning-foreground ring-1 ring-warning/40"
          >
            {degradedRail}
          </Badge>
          <span className="text-muted-foreground">{reason}</span>
          <span className="text-muted-foreground">→</span>
          <span className="text-muted-foreground">prefer</span>
          <Badge
            variant="outline"
            className="px-2.5 py-0.5 text-xs bg-success/25 text-success-foreground ring-1 ring-success/40"
          >
            {preferredRail}
          </Badge>
          <span className="text-muted-foreground">for next</span>
          <Badge
            variant="outline"
            className="px-2.5 py-0.5 text-xs bg-primary/25 text-primary-foreground ring-1 ring-primary/40"
          >
            {windowLabel}
          </Badge>
        </div>
      </AlertDescription>
    </Alert>
  )
}
