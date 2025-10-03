"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Alert, AlertDescription } from "@/components/ui/alert"
import {
  ChartContainer,
  ChartLegend,
  ChartLegendContent,
  ChartTooltip,
  ChartTooltipContent,
} from "@/components/ui/chart"
import { Bar, CartesianGrid, ComposedChart, Line, ReferenceLine, XAxis, YAxis, LineChart } from "recharts"
import { TriangleAlert } from "lucide-react"

const successData = [
  { time: "00:00", IMPS: 98, NEFT: 96, RTGS: 99 },
  { time: "06:00", IMPS: 97, NEFT: 94, RTGS: 99 },
  { time: "12:00", IMPS: 99, NEFT: 92, RTGS: 99 },
  { time: "18:00", IMPS: 98, NEFT: 91, RTGS: 99 },
  { time: "24:00", IMPS: 99, NEFT: 93, RTGS: 99 },
]

const latencyData = [
  { time: "00:00", p95: 0.9 },
  { time: "06:00", p95: 1.2 },
  { time: "12:00", p95: 1.6 },
  { time: "18:00", p95: 1.1 },
  { time: "24:00", p95: 1.0 },
]

const penaltyTrend = [
  { time: "T-4h", count: 2, impact: 2 },
  { time: "T-3h", count: 5, impact: 7 },
  { time: "T-2h", count: 9, impact: 16 },
  { time: "T-1h", count: 7, impact: 23 },
  { time: "Now", count: 6, impact: 29 },
]

export default function RailHealthPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-semibold tracking-tight text-balance">Rail Health</h1>
        <p className="text-sm text-muted-foreground text-pretty">Routing intelligence & SRE view</p>
      </div>

      {/* Advisory */}
      <Alert
        className="glass-card glass-warning text-warning-foreground ring-1 ring-warning/45 border-warning/30"
        role="status"
        aria-live="polite"
      >
        <TriangleAlert className="h-4 w-4" />
        <AlertDescription className="text-sm">
          <div className="flex flex-wrap items-center gap-2">
            <span className="font-medium text-warning-foreground/95">Advisories:</span>
            {/* Vivid NEFT chip with ring */}
            <Badge
              variant="outline"
              className="px-2.5 py-0.5 text-xs bg-warning/25 text-warning-foreground ring-1 ring-warning/40"
            >
              NEFT
            </Badge>
            <span className="text-muted-foreground">penalty high, window closing</span>
            <span className="text-muted-foreground">→</span>
            <span className="text-muted-foreground">prefer</span>
            {/* Vivid IMPS chip with ring */}
            <Badge
              variant="outline"
              className="px-2.5 py-0.5 text-xs bg-success/25 text-success-foreground ring-1 ring-success/40"
            >
              IMPS
            </Badge>
            <span className="text-muted-foreground">for next</span>
            {/* More readable time chip */}
            <Badge
              variant="outline"
              className="px-2.5 py-0.5 text-xs bg-primary/25 text-primary-foreground ring-1 ring-primary/40"
            >
              30m
            </Badge>
          </div>
        </AlertDescription>
      </Alert>

      {/* Per-rail success rate (24h) */}
      <Card className="glass-card glass-primary">
        <CardHeader>
          <CardTitle className="flex items-center justify-between">
            <span>Per-rail success rate (24h)</span>
            <span className="text-xs text-muted-foreground">Higher is better</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <ChartContainer
            config={{
              IMPS: { label: "IMPS", color: "hsl(210, 80%, 60%)" },
              NEFT: { label: "NEFT", color: "hsl(20, 90%, 60%)" },
              RTGS: { label: "RTGS", color: "hsl(140, 70%, 55%)" },
            }}
            className="h-[260px]"
          >
            <LineChart data={successData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="time" />
              <YAxis unit="%" />
              <ChartTooltip content={<ChartTooltipContent />} />
              <ChartLegend content={<ChartLegendContent />} />
              <Line
                type="monotone"
                dataKey="IMPS"
                stroke="var(--color-IMPS)"
                strokeWidth={2}
                dot={false}
                strokeLinecap="round"
                strokeLinejoin="round"
              />
              <Line
                type="monotone"
                dataKey="NEFT"
                stroke="var(--color-NEFT)"
                strokeWidth={2}
                dot={false}
                strokeLinecap="round"
                strokeLinejoin="round"
              />
              <Line
                type="monotone"
                dataKey="RTGS"
                stroke="var(--color-RTGS)"
                strokeWidth={2}
                dot={false}
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            </LineChart>
          </ChartContainer>
        </CardContent>
      </Card>

      {/* Penalty trend (Critic) */}
      <Card className="glass-card glass-destructive">
        <CardHeader>
          <CardTitle>Penalty trend (Critic)</CardTitle>
        </CardHeader>
        <CardContent>
          <ChartContainer
            config={{
              count: { label: "# Penalties", color: "hsl(0, 80%, 60%)" },
              impact: { label: "Impact Score", color: "hsl(12, 80%, 62%)" },
            }}
            className="h-[260px]"
          >
            <ComposedChart data={penaltyTrend}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="time" />
              <YAxis />
              <ChartTooltip content={<ChartTooltipContent />} />
              <Bar dataKey="count" fill="var(--color-count)" name="# Penalties" radius={[4, 4, 0, 0]} />
              <Line
                type="monotone"
                dataKey="impact"
                stroke="var(--color-impact)"
                strokeWidth={2}
                dot={false}
                name="Impact Score"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            </ComposedChart>
          </ChartContainer>
        </CardContent>
      </Card>

      {/* p95 dispatch latency (s) */}
      <Card className="glass-card glass-warning">
        <CardHeader>
          <CardTitle>p95 dispatch latency (s)</CardTitle>
        </CardHeader>
        <CardContent>
          <ChartContainer config={{ p95: { label: "Latency (s)", color: "hsl(45, 90%, 60%)" } }} className="h-[260px]">
            <LineChart data={latencyData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="time" />
              <YAxis />
              <ChartTooltip cursor={false} content={<ChartTooltipContent indicator="line" />} />
              <ReferenceLine
                y={2}
                stroke="hsl(0, 80%, 60%)"
                strokeDasharray="6 6"
                label={{ value: "SLA 2s", position: "right", fill: "hsl(0,80%,60%)" }}
              />
              <Line
                type="monotone"
                dataKey="p95"
                stroke="var(--color-p95)"
                strokeWidth={2}
                dot={false}
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            </LineChart>
          </ChartContainer>
        </CardContent>
      </Card>

      {/* Cut-off timers */}
      <Card className="glass-card glass-primary">
        <CardHeader>
          <CardTitle>Cut-off timers</CardTitle>
        </CardHeader>
        <CardContent>
          <ul className="grid grid-cols-1 gap-3 md:grid-cols-3">
            {[
              { rail: "NEFT", cutoff: "In 22m", tone: "warning" },
              { rail: "RTGS", cutoff: "In 2h 10m", tone: "default" },
              { rail: "IMPS", cutoff: "No cut-off", tone: "success" },
            ].map((c) => (
              <li key={c.rail} className="rounded-lg border p-3">
                <div className="flex items-center justify-between">
                  <span className="text-sm">{c.rail}</span>
                  <Badge
                    variant="outline"
                    className={
                      c.tone === "warning"
                        ? "bg-warning/25 text-warning-foreground ring-1 ring-warning/40"
                        : c.tone === "success"
                          ? "bg-success/25 text-success-foreground ring-1 ring-success/40"
                          : "bg-muted text-muted-foreground"
                    }
                  >
                    {c.cutoff}
                  </Badge>
                </div>
              </li>
            ))}
          </ul>
        </CardContent>
      </Card>
    </div>
  )
}
