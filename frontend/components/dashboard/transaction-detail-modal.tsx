import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { Badge } from "@/components/ui/badge"
import { CheckCircle2, AlertTriangle, Clock, FileText } from "lucide-react"

interface TransactionDetailModalProps {
  transactionId: string | null
  open: boolean
  onClose: () => void
}

const transactionLogs = [
  {
    timestamp: "2025-09-29 10:15:23",
    agent: "ACC Agent",
    action: "HOLD",
    reason: "IFSC_TYPO",
    policy: "acc-v1.4.2",
    evidence: "s3://evidence/acc-12345678.json",
    icon: AlertTriangle,
    color: "text-primary",
  },
  {
    timestamp: "2025-09-29 10:18:45",
    agent: "Operator",
    action: "Manual Fix Applied",
    reason: "Corrected IFSC code from HDFC0001234 to HDFC0001235",
    policy: "N/A",
    evidence: "operator-log-456",
    icon: CheckCircle2,
    color: "text-primary",
  },
  {
    timestamp: "2025-09-29 10:19:12",
    agent: "ACC Agent",
    action: "PASS",
    reason: "All compliance checks passed",
    policy: "acc-v1.4.2",
    evidence: "s3://evidence/acc-12345678-v2.json",
    icon: CheckCircle2,
    color: "text-primary",
  },
  {
    timestamp: "2025-09-29 10:19:45",
    agent: "PDR Agent",
    action: "Route Selected",
    reason: "IMPS@HDFC selected. Fallback: NEFT",
    policy: "pdr-v1.2.1",
    evidence: "s3://evidence/pdr-12345678.json",
    icon: Clock,
    color: "text-primary",
  },
]

export function TransactionDetailModal({ transactionId, open, onClose }: TransactionDetailModalProps) {
  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className="max-w-3xl bg-slate-900 border-slate-800 text-white">
        <DialogHeader>
          <DialogTitle className="text-xl">Transaction Lineage & Evidence</DialogTitle>
          <p className="text-sm text-slate-400">Transaction ID: {transactionId}</p>
        </DialogHeader>

        <div className="space-y-4 max-h-[500px] overflow-y-auto">
          {transactionLogs.map((log, index) => {
            const Icon = log.icon
            return (
              <div key={index} className="relative pl-8 pb-6 border-l-2 border-slate-700 last:border-0 last:pb-0">
                <div className={`absolute left-0 -translate-x-1/2 rounded-full bg-slate-900 p-1 ${log.color}`}>
                  <Icon className="h-4 w-4" />
                </div>
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <span className="font-semibold text-slate-200">{log.agent}</span>
                      <Badge variant="outline" className="text-xs">
                        {log.action}
                      </Badge>
                    </div>
                    <span className="text-xs text-slate-500">{log.timestamp}</span>
                  </div>
                  <p className="text-sm text-slate-300">{log.reason}</p>
                  <div className="flex items-center gap-4 text-xs text-slate-500">
                    <span>Policy: {log.policy}</span>
                    <a href="#" className="flex items-center gap-1 text-primary hover:underline">
                      <FileText className="h-3 w-3" />
                      Evidence
                    </a>
                  </div>
                </div>
              </div>
            )
          })}
        </div>
      </DialogContent>
    </Dialog>
  )
}
