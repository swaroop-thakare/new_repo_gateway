import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import { Stepper } from "./stepper"

export function BatchCard({
  id,
  date,
  name,
  entity,
  amount,
  status,
  href,
  actionLabel = "View",
}: {
  id: string
  date: string
  name: string
  entity: string
  amount: string
  status: string
  href: string
  actionLabel?: string
}) {
  return (
    <Card>
      <CardContent className="flex flex-col gap-4 p-4 sm:flex-row sm:items-center sm:justify-between">
        <div className="min-w-0">
          <div className="text-sm text-slate-500">{date}</div>
          <div className="text-lg font-semibold">{name}</div>
          <div className="text-sm text-slate-600">{entity}</div>
          <div className="mt-3">
            <Stepper
              steps={[
                { label: "Data Ingested", status: "done" },
                { label: "Compliance Check", status: status === "In Progress" ? "current" : "done" },
                { label: "Awaiting Approval", status: "pending" },
                { label: "Processing", status: "pending" },
                { label: "Completed", status: "pending" },
              ]}
            />
          </div>
        </div>

        <div className="flex shrink-0 items-center gap-6">
          <div className="text-right">
            <div className="text-xs text-slate-500">Total Amount</div>
            <div className="text-base font-semibold">{amount}</div>
          </div>
          <div className="text-right">
            <div className="text-xs text-slate-500">Status</div>
            <div className="text-base font-semibold">{status}</div>
          </div>
          <Button asChild>
            <Link href={href}>{actionLabel}</Link>
          </Button>
        </div>
      </CardContent>
    </Card>
  )
}
