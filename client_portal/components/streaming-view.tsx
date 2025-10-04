"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { ArrowLeft, Loader2, CheckCircle2, Circle, LinkIcon } from "lucide-react"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"

interface StreamingViewProps {
  onBack: () => void
}

type IngestionStep = {
  label: string
  completed: boolean
}

type Transaction = {
  id: string
  lineId: string
  beneficiary: string
  ifsc: string
  amount: number
  policyVersion: string
  decision: "PASS" | "HOLD" | "FAIL"
  decisionReason: string
  evidenceRef: string
}

const INGESTION_STEPS = [
  "Fetching data...",
  "Processing the data...",
  "Clean and deduplication of data...",
  "Validating the schema...",
  "Mapping the schema into proper format...",
]

const SAMPLE_TRANSACTIONS: Transaction[] = [
  {
    id: "TXN-001",
    lineId: "L-001",
    beneficiary: "Acme Corp Ltd",
    ifsc: "HDFC0001234",
    amount: 125000,
    policyVersion: "v2.1",
    decision: "PASS",
    decisionReason: "All checks passed",
    evidenceRef: "EV-2025-001",
  },
  {
    id: "TXN-002",
    lineId: "L-002",
    beneficiary: "Tech Solutions Inc",
    ifsc: "ICIC0005678",
    amount: 87500,
    policyVersion: "v2.1",
    decision: "HOLD",
    decisionReason: "Pending verification",
    evidenceRef: "EV-2025-002",
  },
  {
    id: "TXN-003",
    lineId: "L-003",
    beneficiary: "Global Traders",
    ifsc: "SBIN0009876",
    amount: 250000,
    policyVersion: "v2.1",
    decision: "PASS",
    decisionReason: "All checks passed",
    evidenceRef: "EV-2025-003",
  },
  {
    id: "TXN-004",
    lineId: "L-004",
    beneficiary: "Metro Services",
    ifsc: "AXIS0002345",
    amount: 45000,
    policyVersion: "v2.0",
    decision: "FAIL",
    decisionReason: "Invalid account details",
    evidenceRef: "EV-2025-004",
  },
  {
    id: "TXN-005",
    lineId: "L-005",
    beneficiary: "Prime Logistics",
    ifsc: "HDFC0003456",
    amount: 156000,
    policyVersion: "v2.1",
    decision: "PASS",
    decisionReason: "All checks passed",
    evidenceRef: "EV-2025-005",
  },
  {
    id: "TXN-006",
    lineId: "L-006",
    beneficiary: "Swift Enterprises",
    ifsc: "ICIC0007890",
    amount: 92000,
    policyVersion: "v2.1",
    decision: "HOLD",
    decisionReason: "Amount threshold review",
    evidenceRef: "EV-2025-006",
  },
  {
    id: "TXN-007",
    lineId: "L-007",
    beneficiary: "Zenith Industries",
    ifsc: "SBIN0001122",
    amount: 310000,
    policyVersion: "v2.1",
    decision: "PASS",
    decisionReason: "All checks passed",
    evidenceRef: "EV-2025-007",
  },
  {
    id: "TXN-008",
    lineId: "L-008",
    beneficiary: "Apex Manufacturing",
    ifsc: "AXIS0004567",
    amount: 67500,
    policyVersion: "v2.1",
    decision: "PASS",
    decisionReason: "All checks passed",
    evidenceRef: "EV-2025-008",
  },
]

export function StreamingView({ onBack }: StreamingViewProps) {
  const [phase, setPhase] = useState<"link-input" | "ingestion" | "streaming">("link-input")
  const [streamLink, setStreamLink] = useState("")
  const [steps, setSteps] = useState<IngestionStep[]>(INGESTION_STEPS.map((label) => ({ label, completed: false })))
  const [currentStepIndex, setCurrentStepIndex] = useState(0)
  const [ingestionComplete, setIngestionComplete] = useState(false)
  const [transactions, setTransactions] = useState<Transaction[]>([])
  const [streamComplete, setStreamComplete] = useState(false)

  const handleStartIngestion = () => {
    if (streamLink.trim()) {
      setPhase("ingestion")
    }
  }

  useEffect(() => {
    if (phase === "ingestion" && currentStepIndex < INGESTION_STEPS.length) {
      const timer = setTimeout(() => {
        setSteps((prev) => prev.map((step, idx) => (idx === currentStepIndex ? { ...step, completed: true } : step)))
        setCurrentStepIndex((prev) => prev + 1)
      }, 800)

      return () => clearTimeout(timer)
    } else if (phase === "ingestion" && currentStepIndex === INGESTION_STEPS.length) {
      setIngestionComplete(true)
      const timer = setTimeout(() => {
        setPhase("streaming")
      }, 1000)
      return () => clearTimeout(timer)
    }
  }, [phase, currentStepIndex])

  useEffect(() => {
    if (phase === "streaming" && transactions.length < SAMPLE_TRANSACTIONS.length) {
      const timer = setTimeout(() => {
        setTransactions((prev) => [...prev, SAMPLE_TRANSACTIONS[prev.length]])
      }, 600)

      return () => clearTimeout(timer)
    } else if (phase === "streaming" && transactions.length === SAMPLE_TRANSACTIONS.length) {
      const timer = setTimeout(() => {
        setStreamComplete(true)
      }, 500)
      return () => clearTimeout(timer)
    }
  }, [phase, transactions])

  const getDecisionBadge = (decision: Transaction["decision"]) => {
    const variants = {
      PASS: "bg-green-500/20 text-green-400 border-green-500/30",
      HOLD: "bg-yellow-500/20 text-yellow-400 border-yellow-500/30",
      FAIL: "bg-red-500/20 text-red-400 border-red-500/30",
    }

    return (
      <Badge variant="outline" className={`${variants[decision]} font-medium`}>
        {decision}
      </Badge>
    )
  }

  if (phase === "link-input") {
    return (
      <div className="max-w-2xl mx-auto">
        <Button variant="ghost" onClick={onBack} className="mb-4">
          <ArrowLeft className="w-4 h-4 mr-2" />
          Back to Selection
        </Button>

        <Card className="shadow-lg bg-card">
          <CardHeader className="text-center pb-6">
            <CardTitle className="text-2xl font-semibold">Real-time Data Streaming</CardTitle>
            <p className="text-muted-foreground mt-2">Enter the stream endpoint URL to begin ingestion</p>
          </CardHeader>

          <CardContent className="space-y-6 pb-8">
            <div className="flex justify-center">
              <div className="w-16 h-16 rounded-full bg-primary/20 flex items-center justify-center">
                <LinkIcon className="w-8 h-8 text-primary" />
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="stream-link" className="text-base">
                Stream Endpoint URL
              </Label>
              <Input
                id="stream-link"
                type="url"
                placeholder="https://api.example.com/stream/endpoint"
                value={streamLink}
                onChange={(e) => setStreamLink(e.target.value)}
                className="h-12 text-base"
              />
              <p className="text-sm text-muted-foreground">
                Provide the URL endpoint that will stream transaction data in real-time
              </p>
            </div>

            <Button
              onClick={handleStartIngestion}
              disabled={!streamLink.trim()}
              className="w-full h-12 text-base font-medium"
            >
              Begin Live Stream
            </Button>
          </CardContent>
        </Card>
      </div>
    )
  }

  if (phase === "ingestion") {
    return (
      <div className="max-w-2xl mx-auto">
        <Button variant="ghost" onClick={onBack} className="mb-4">
          <ArrowLeft className="w-4 h-4 mr-2" />
          Back to Selection
        </Button>

        <Card className="shadow-lg bg-card">
          <CardHeader className="text-center pb-6">
            <CardTitle className="text-2xl font-semibold">Real-time Data Processing</CardTitle>
          </CardHeader>

          <CardContent className="space-y-8 pb-8">
            <div className="flex justify-center">
              <div className="w-16 h-16 rounded-full bg-primary/20 flex items-center justify-center">
                <Loader2 className="w-8 h-8 text-primary animate-spin" />
              </div>
            </div>

            <div className="space-y-4">
              {steps.map((step, index) => (
                <div key={index} className="flex items-center gap-4">
                  <div className="flex-shrink-0">
                    {step.completed ? (
                      <CheckCircle2 className="w-6 h-6 text-green-500" />
                    ) : (
                      <Circle className="w-6 h-6 text-muted-foreground" />
                    )}
                  </div>
                  <p className={`text-base ${step.completed ? "text-foreground" : "text-muted-foreground"}`}>
                    {step.label}
                  </p>
                </div>
              ))}
            </div>

            <div className="text-center pt-4">
              <p className={`text-lg font-medium ${ingestionComplete ? "text-green-500" : "text-muted-foreground"}`}>
                {ingestionComplete ? "Ingestion completed" : "Ingestion in process..."}
              </p>
            </div>
          </CardContent>
        </Card>
      </div>
    )
  }

  return (
    <div className="max-w-7xl mx-auto">
      <Button variant="ghost" onClick={onBack} className="mb-4">
        <ArrowLeft className="w-4 h-4 mr-2" />
        Back to Selection
      </Button>

      <Card className="shadow-lg">
        <CardHeader className="pb-6">
          <div className="flex items-center justify-between">
            <CardTitle className="text-2xl font-semibold">Transaction Data Stream</CardTitle>
            <Badge variant="destructive" className="bg-red-500 text-white">
              <span className="w-2 h-2 bg-white rounded-full mr-2 animate-pulse" />
              Live
            </Badge>
          </div>
        </CardHeader>

        <CardContent>
          <div className="rounded-lg border overflow-hidden">
            <Table>
              <TableHeader>
                <TableRow className="bg-muted/50">
                  <TableHead className="font-semibold">ID</TableHead>
                  <TableHead className="font-semibold">Line ID</TableHead>
                  <TableHead className="font-semibold">Beneficiary</TableHead>
                  <TableHead className="font-semibold">IFSC</TableHead>
                  <TableHead className="font-semibold">Amount</TableHead>
                  <TableHead className="font-semibold">Policy Version</TableHead>
                  <TableHead className="font-semibold">Decision</TableHead>
                  <TableHead className="font-semibold">Decision Reason</TableHead>
                  <TableHead className="font-semibold">Evidence Ref</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {transactions.map((txn, index) => (
                  <TableRow key={txn.id} className="animate-in fade-in slide-in-from-top-2 duration-300">
                    <TableCell className="font-medium">{txn.id}</TableCell>
                    <TableCell>{txn.lineId}</TableCell>
                    <TableCell>{txn.beneficiary}</TableCell>
                    <TableCell className="font-mono text-sm">{txn.ifsc}</TableCell>
                    <TableCell>₹{txn.amount.toLocaleString("en-IN")}</TableCell>
                    <TableCell className="font-mono text-sm">{txn.policyVersion}</TableCell>
                    <TableCell>{getDecisionBadge(txn.decision)}</TableCell>
                    <TableCell className="text-sm text-muted-foreground">{txn.decisionReason}</TableCell>
                    <TableCell className="font-mono text-sm">{txn.evidenceRef}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>

          {streamComplete && (
            <div className="flex justify-center mt-6">
              <Badge variant="outline" className="bg-green-500/20 text-green-400 border-green-500/30 px-4 py-2">
                <CheckCircle2 className="w-4 h-4 mr-2" />
                Ingestion completed
              </Badge>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
