"use client"

import { X, ChevronRight, Download, RefreshCw } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Badge } from "@/components/ui/badge"
import { ScrollArea } from "@/components/ui/scroll-area"

interface AgentDrawerProps {
  isOpen: boolean
  onClose: () => void
  traceId?: string
  defaultTab?: "summary" | "why" | "bundle" | "toolplan" | "actions" | "logs"
}

export function AgentDrawer({
  isOpen,
  onClose,
  traceId = "TRC-2024-001234",
  defaultTab = "summary",
}: AgentDrawerProps) {
  if (!isOpen) return null

  return (
    <div className="fixed right-0 top-0 z-50 h-screen w-[520px] border-l border-white/10 bg-[#0d0d0d] shadow-2xl">
      {/* Header */}
      <div className="flex h-16 items-center justify-between border-b border-white/5 px-6">
        <div>
          <h3 className="text-base font-semibold tracking-tight text-white">Agent Console</h3>
          <p className="font-mono text-xs text-gray-400">{traceId}</p>
        </div>
        <Button
          variant="ghost"
          size="icon"
          onClick={onClose}
          className="text-gray-400 hover:bg-white/5 hover:text-white"
        >
          <X className="h-5 w-5" />
        </Button>
      </div>

      {/* Tabs */}
      <Tabs defaultValue={defaultTab} className="flex h-[calc(100vh-4rem)] flex-col">
        <TabsList className="w-full justify-start rounded-none border-b border-white/5 bg-transparent p-0">
          <TabsTrigger
            value="summary"
            className="rounded-none border-b-2 border-transparent text-gray-400 data-[state=active]:border-blue-500 data-[state=active]:bg-transparent data-[state=active]:text-white"
          >
            Summary
          </TabsTrigger>
          <TabsTrigger
            value="why"
            className="rounded-none border-b-2 border-transparent text-gray-400 data-[state=active]:border-blue-500 data-[state=active]:bg-transparent data-[state=active]:text-white"
          >
            Why?
          </TabsTrigger>
          <TabsTrigger
            value="bundle"
            className="rounded-none border-b-2 border-transparent text-gray-400 data-[state=active]:border-blue-500 data-[state=active]:bg-transparent data-[state=active]:text-white"
          >
            Bundle
          </TabsTrigger>
          <TabsTrigger
            value="toolplan"
            className="rounded-none border-b-2 border-transparent text-gray-400 data-[state=active]:border-blue-500 data-[state=active]:bg-transparent data-[state=active]:text-white"
          >
            ToolPlan
          </TabsTrigger>
          <TabsTrigger
            value="actions"
            className="rounded-none border-b-2 border-transparent text-gray-400 data-[state=active]:border-blue-500 data-[state=active]:bg-transparent data-[state=active]:text-white"
          >
            Actions
          </TabsTrigger>
          <TabsTrigger
            value="logs"
            className="rounded-none border-b-2 border-transparent text-gray-400 data-[state=active]:border-blue-500 data-[state=active]:bg-transparent data-[state=active]:text-white"
          >
            Logs
          </TabsTrigger>
        </TabsList>

        <ScrollArea className="flex-1">
          <TabsContent value="summary" className="m-0 p-6">
            <div className="space-y-6">
              <div>
                <h4 className="mb-4 text-sm font-semibold tracking-tight text-white">Decision Story</h4>
                <div className="space-y-3">
                  <TimelineItem
                    time="10:23:45"
                    status="success"
                    title="Context Validated"
                    description="Payment request validated against policy v2.3"
                  />
                  <TimelineItem
                    time="10:23:46"
                    status="success"
                    title="ACC Passed"
                    description="Anti-money laundering checks cleared"
                  />
                  <TimelineItem
                    time="10:23:47"
                    status="success"
                    title="Rail Selected"
                    description="IMPS selected (cost: ₹5, ETA: 2min)"
                  />
                  <TimelineItem
                    time="10:23:50"
                    status="pending"
                    title="Awaiting Dispatch"
                    description="Queued for next release window"
                  />
                </div>
              </div>

              <div className="space-y-3 rounded-lg border border-white/10 bg-white/5 p-4">
                <div className="flex justify-between text-sm">
                  <span className="text-gray-400">Amount</span>
                  <span className="font-semibold text-white">₹25,000</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-400">Beneficiary</span>
                  <span className="font-medium text-gray-300">Vendor Corp (****4567)</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-400">Selected Rail</span>
                  <Badge
                    variant="outline"
                    className="border-blue-500/30 bg-blue-500/20 font-mono text-xs text-blue-400"
                  >
                    IMPS
                  </Badge>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-400">Urgency</span>
                  <Badge className="bg-yellow-500/20 text-yellow-400">High</Badge>
                </div>
              </div>
            </div>
          </TabsContent>

          <TabsContent value="why" className="m-0 p-6">
            <div className="space-y-4">
              <div>
                <h4 className="mb-2 font-semibold text-white">Why IMPS was selected?</h4>
                <div className="space-y-2 text-sm text-gray-300">
                  <p>
                    <strong className="text-white">Primary factors:</strong>
                  </p>
                  <ul className="ml-4 list-disc space-y-1">
                    <li>High urgency flag set by requester</li>
                    <li>NEFT window closing in 15 minutes</li>
                    <li>IMPS success rate: 99.2% (last 24h)</li>
                    <li>Cost difference: ₹5 vs ₹8 (RTGS)</li>
                    <li>Expected settlement: 2 minutes vs 30 minutes</li>
                  </ul>
                  <p className="mt-3">
                    <strong className="text-white">Policy reference:</strong> POL-2024-003 (Urgency-based routing)
                  </p>
                </div>
              </div>

              <div className="rounded-lg border border-blue-500/30 bg-blue-500/10 p-4">
                <p className="text-sm text-blue-300">
                  <strong>Critic Score:</strong> IMPS penalty is low (0.02) based on recent performance. No re-selection
                  needed.
                </p>
              </div>
            </div>
          </TabsContent>

          <TabsContent value="bundle" className="m-0 p-6">
            <div className="space-y-4">
              <p className="text-sm text-gray-400">Context Bundle (sanitized for PII protection)</p>
              <pre className="overflow-x-auto rounded-lg border border-white/10 bg-black p-4 text-xs text-gray-300">
                {`{
  "trace_id": "TRC-2024-001234",
  "amount": 25000,
  "currency": "INR",
  "beneficiary": {
    "account": "****4567",
    "ifsc": "HDFC0001234",
    "name": "[REDACTED]"
  },
  "urgency": "high",
  "policy_version": "v2.3",
  "acc_result": "PASS",
  "rail_candidates": ["IMPS", "NEFT", "RTGS"],
  "deadline": "2024-01-15T11:00:00Z"
}`}
              </pre>
            </div>
          </TabsContent>

          <TabsContent value="toolplan" className="m-0 p-6">
            <div className="space-y-4">
              <div>
                <h4 className="mb-2 font-semibold text-white">Allowed Tools</h4>
                <div className="space-y-2">
                  <ToolItem name="select_rail" status="allowed" />
                  <ToolItem name="request_approval" status="allowed" />
                  <ToolItem name="emit_to_queue" status="allowed" />
                  <ToolItem name="dispatch" status="blocked" reason="Requires approval first" />
                </div>
              </div>

              <div>
                <h4 className="mb-2 font-semibold text-white">Invariants</h4>
                <ul className="space-y-1 text-sm text-gray-300">
                  <li>✓ No dispatch before approval for amounts ≥ ₹10,000</li>
                  <li>✓ Pre-commit rail shift only</li>
                  <li>✓ Idempotency key required for all writes</li>
                  <li>✓ PII masking enforced in logs</li>
                </ul>
              </div>
            </div>
          </TabsContent>

          <TabsContent value="actions" className="m-0 p-6">
            <div className="space-y-3">
              <Button
                variant="outline"
                className="w-full justify-start gap-2 border-white/10 bg-white/5 text-white hover:bg-white/10"
              >
                <RefreshCw className="h-4 w-4" />
                Request Re-score
              </Button>
              <Button
                variant="outline"
                className="w-full justify-start gap-2 border-white/10 bg-white/5 text-white hover:bg-white/10"
              >
                <Download className="h-4 w-4" />
                Download Audit Pack
              </Button>
              <Button
                variant="outline"
                className="w-full justify-start gap-2 border-white/10 bg-white/5 text-white hover:bg-white/10"
              >
                <ChevronRight className="h-4 w-4" />
                Open Ledger View
              </Button>
            </div>
          </TabsContent>

          <TabsContent value="logs" className="m-0 p-6">
            <div className="space-y-2">
              <LogEntry time="10:23:45.123" event="context_validated" status="success" />
              <LogEntry time="10:23:46.456" event="acc_check_started" status="success" />
              <LogEntry time="10:23:46.789" event="acc_check_passed" status="success" />
              <LogEntry time="10:23:47.012" event="pdr_rail_selection" status="success" />
              <LogEntry time="10:23:47.345" event="emit_to_release_queue" status="success" />
              <LogEntry time="10:23:50.678" event="awaiting_dispatch_window" status="pending" />
            </div>
          </TabsContent>
        </ScrollArea>
      </Tabs>
    </div>
  )
}

function TimelineItem({
  time,
  status,
  title,
  description,
}: {
  time: string
  status: "success" | "pending" | "error"
  title: string
  description: string
}) {
  const colors = {
    success: "bg-blue-500",
    pending: "bg-yellow-500",
    error: "bg-red-500",
  }

  return (
    <div className="flex gap-3">
      <div className="flex flex-col items-center">
        <div className={`h-2 w-2 rounded-full ${colors[status]} ring-4 ring-${status}/10`} />
        <div className="w-px flex-1 bg-white/10" />
      </div>
      <div className="flex-1 pb-4">
        <div className="flex items-center gap-2">
          <span className="font-mono text-xs text-gray-400">{time}</span>
          <span className="text-sm font-semibold text-white">{title}</span>
        </div>
        <p className="mt-1 text-sm text-gray-400">{description}</p>
      </div>
    </div>
  )
}

function ToolItem({ name, status, reason }: { name: string; status: "allowed" | "blocked"; reason?: string }) {
  return (
    <div className="rounded border border-white/10 bg-white/5 p-3">
      <div className="flex items-center justify-between">
        <code className="text-sm text-gray-300">{name}</code>
        <div className="flex items-center gap-2">
          {status === "allowed" ? (
            <Badge variant="outline" className="border-green-500/30 bg-green-500/10 text-green-400">
              Allowed
            </Badge>
          ) : (
            <Badge variant="outline" className="border-red-500/30 bg-red-500/10 text-red-400">
              Blocked
            </Badge>
          )}
        </div>
      </div>
      {reason && <p className="mt-1 text-xs text-gray-500">{reason}</p>}
    </div>
  )
}

function LogEntry({ time, event, status }: { time: string; event: string; status: "success" | "pending" | "error" }) {
  const colors = {
    success: "text-blue-400",
    pending: "text-yellow-400",
    error: "text-red-400",
  }

  return (
    <div className="flex items-start gap-2 rounded border border-white/10 bg-white/5 p-2 text-xs font-mono">
      <span className="text-gray-500">{time}</span>
      <span className={colors[status]}>{event}</span>
    </div>
  )
}
