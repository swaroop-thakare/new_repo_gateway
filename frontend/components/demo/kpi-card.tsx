import { Card, CardContent } from "@/components/ui/card"
import { cn } from "@/lib/utils"
import { ArrowUpRight, ArrowDownRight, Minus } from "lucide-react"

type Trend = "up" | "down" | "flat"

export function KpiCard({
  label,
  value,
  delta,
  trend = "flat",
  className,
}: {
  label: string
  value: string
  delta?: string
  trend?: Trend
  className?: string
}) {
  const trendColor = trend === "up" ? "text-primary" : trend === "down" ? "text-red-500" : "text-muted-foreground"
  const TrendIcon = trend === "up" ? ArrowUpRight : trend === "down" ? ArrowDownRight : Minus

  return (
    <Card className={cn("glass-card glass-primary transition-transform hover:-translate-y-0.5", className)}>
      <CardContent className="p-5">
        <p className="text-[11px] uppercase tracking-wide text-muted-foreground">{label}</p>
        <div className="mt-1 flex items-center gap-2">
          <span className="text-xl font-semibold">{value}</span>
          {delta ? <span className={cn("text-xs", trendColor)}>{delta}</span> : null}
          <TrendIcon className={cn("h-3 w-3", trendColor)} aria-hidden="true" />
        </div>
      </CardContent>
    </Card>
  )
}
