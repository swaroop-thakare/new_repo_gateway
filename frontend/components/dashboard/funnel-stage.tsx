"use client"

type Props = {
  label: string
  count: number
  percentage: number
  width: number // 0-100
  dropoff: number | null
}

export default function FunnelStage({ label, count, percentage, width, dropoff }: Props) {
  const clamped = Math.max(0, Math.min(100, width))

  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between text-sm">
        <span className="font-medium text-white">{label}</span>
        <div className="flex items-center gap-2">
          {dropoff !== null ? (
            <span className="rounded px-1.5 py-0.5 text-[11px] text-red-400">-{dropoff}%</span>
          ) : null}
          <span className="text-xs text-gray-400">
            {count.toLocaleString()} • {percentage}%
          </span>
        </div>
      </div>
      <div
        className="h-3 w-full rounded-md bg-white/10"
        role="progressbar"
        aria-valuenow={clamped}
        aria-valuemin={0}
        aria-valuemax={100}
        aria-label={`${label} completion`}
      >
        <div className="h-full rounded-md bg-blue-500/70" style={{ width: `${clamped}%` }} />
      </div>
    </div>
  )
}
