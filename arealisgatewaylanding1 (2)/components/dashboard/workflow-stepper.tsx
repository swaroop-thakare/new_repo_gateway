import { CheckCircle2, Clock, AlertTriangle, Circle, XCircle } from "lucide-react"
import { cn } from "@/lib/utils"

const steps = [
  { label: "Ingestion", status: "completed" },
  { label: "Credit & Risk Assessment", status: "completed" },
  { label: "Compliance (ACC)", status: "warning" },
  { label: "Operator Review", status: "in-progress" },
  { label: "Routing (PDR)", status: "pending" },
  { label: "Admin Approval", status: "pending" },
  { label: "Execution", status: "pending" },
  { label: "Reconciliation (ARL)", status: "pending" },
  { label: "Audit Pack (CRRAK)", status: "pending" },
]

export function WorkflowStepper() {
  const getStatusIcon = (status: string) => {
    switch (status) {
      case "completed":
        return <CheckCircle2 className="h-6 w-6 text-primary" />
      case "in-progress":
        return <Clock className="h-6 w-6 text-blue-500 animate-pulse" />
      case "warning":
        return <AlertTriangle className="h-6 w-6 text-amber-500" />
      case "failed":
        return <XCircle className="h-6 w-6 text-red-500" />
      default:
        return <Circle className="h-6 w-6 text-slate-600" />
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case "completed":
        return "border-primary"
      case "in-progress":
        return "border-blue-500"
      case "warning":
        return "border-amber-500"
      case "failed":
        return "border-red-500"
      default:
        return "border-slate-700"
    }
  }

  return (
    <div className="relative">
      <div className="flex items-start justify-between gap-2 overflow-x-auto pb-4">
        {steps.map((step, index) => (
          <div key={index} className="flex flex-col items-center min-w-[100px]">
            <div
              className={cn(
                "flex h-12 w-12 items-center justify-center rounded-full border-2 bg-slate-900",
                getStatusColor(step.status),
              )}
            >
              {getStatusIcon(step.status)}
            </div>
            <div className="mt-2 text-center">
              <p className="text-xs font-medium text-slate-200">{step.label}</p>
              <p className="text-xs text-slate-500 capitalize">{step.status.replace("-", " ")}</p>
            </div>
            {index < steps.length - 1 && (
              <div
                className="absolute top-6 left-0 right-0 h-0.5 bg-slate-700 -z-10"
                style={{ width: `${(100 / steps.length) * (index + 1)}%` }}
              />
            )}
          </div>
        ))}
      </div>
    </div>
  )
}
