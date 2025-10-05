import { CheckCircle2, Clock } from "lucide-react"

type Step = { label: string; status?: "done" | "current" | "pending" | "warning" }
export function Stepper({ steps }: { steps: Step[] }) {
  return (
    <div className="flex flex-wrap items-center gap-3">
      {steps.map((s, i) => (
        <div key={s.label} className="flex items-center gap-3">
          <div
            className={[
              "flex h-7 w-7 items-center justify-center rounded-full border text-xs",
              s.status === "done" ? "bg-blue-600 text-white border-blue-600" : "",
              s.status === "current" ? "border-blue-600 text-blue-700" : "",
              !s.status || s.status === "pending" ? "border-slate-300 text-slate-500 bg-white" : "",
            ].join(" ")}
            aria-label={`${s.label} ${s.status ?? "pending"}`}
          >
            {s.status === "done" ? (
              <CheckCircle2 className="h-4 w-4" />
            ) : s.status === "current" ? (
              <Clock className="h-4 w-4" />
            ) : (
              i + 1
            )}
          </div>
          <div className="text-sm">{s.label}</div>
          {i < steps.length - 1 && <div className="h-px w-8 bg-slate-300" aria-hidden="true" />}
        </div>
      ))}
    </div>
  )
}
