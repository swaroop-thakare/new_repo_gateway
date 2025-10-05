"use client"

import React, { useState, useMemo, useEffect } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Drawer, DrawerContent, DrawerHeader, DrawerTitle, DrawerDescription } from "@/components/ui/drawer"
import { FileDown, FileText, BookOpen, Share2 } from "lucide-react"
import { Input } from "@/components/ui/input"
import { Select, SelectTrigger, SelectContent, SelectItem, SelectValue } from "@/components/ui/select"
import { useTransactions } from "@/hooks/use-api"

// CRRAK Audit Filing interface
interface CRRAKAuditFiling {
  trace: string
  status: "Ready" | "Pending" | "Failed"
  bankFmt: string
  regulatorFmt: string
  utr: string
  crrakResult?: {
    compliance_status: string
    combined_details: any
    neo4j_state: string
    report_ref: string
  }
}

const filings = [
  { trace: "TRC-2024-001231", status: "Ready", bankFmt: "CSV", regulatorFmt: "PDF", utr: "UTR2024001230456" },
  { trace: "TRC-2024-001228", status: "Pending", bankFmt: "XML", regulatorFmt: "PDF", utr: "—" },
  { trace: "TRC-2024-001255", status: "Failed", bankFmt: "CSV", regulatorFmt: "PDF", utr: "—" },
  { trace: "TRC-2024-001240", status: "Ready", bankFmt: "CSV", regulatorFmt: "PDF", utr: "UTR2024001230457" },
]

export default function AuditFilingsPage() {
  const { transactions, loading, error } = useTransactions()
  const [open, setOpen] = useState(false)
  const [activeTrace, setActiveTrace] = useState<string | null>(null)
  const [q, setQ] = useState("")
  const [status, setStatus] = useState<"All" | "Ready" | "Pending" | "Failed">("All")
  const [page, setPage] = useState(1)
  const pageSize = 8
  const [crrakAuditData, setCrrakAuditData] = useState<CRRAKAuditFiling[]>([])

  // Function to fetch CRRAK audit data
  const fetchCRRAKAuditData = async () => {
    try {
      // Call the CRRAK service API for real audit data
      const crrakPromises = transactions.slice(0, 10).map(async (tx, index) => {
        try {
          const response = await fetch('http://localhost:8010/api/v1/process', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({
              batch_id: `B-${tx.id}`,
              line_id: `L${index + 1}`,
              arl_data: {
                status: tx.status === "completed" ? "RECONCILED" : "PENDING",
                matched: tx.status === "completed" ? [{line_id: `L${index + 1}`, utr: `UTR${tx.id}`}] : [],
                exceptions: tx.status === "failed" ? ["Transaction failed"] : []
              },
              rca_data: tx.status === "failed" ? {
                root_cause: "Transaction failure",
                fault_party: "System",
                retry_eligible: false,
                priority_score: 50
              } : null
            })
          })

          if (response.ok) {
            const crrakResult = await response.json()
            return {
              trace: tx.id,
              status: crrakResult.compliance_status === "COMPLIANT" ? "Ready" as const : 
                     crrakResult.compliance_status === "PENDING" ? "Pending" as const : "Failed" as const,
              bankFmt: "CSV",
              regulatorFmt: "PDF",
              utr: tx.status === "completed" ? tx.reference : "—",
              crrakResult: crrakResult
            }
          }
        } catch (error) {
          console.error(`Failed to fetch CRRAK data for transaction ${tx.id}:`, error)
        }

        // Fallback to basic audit filing
        return {
          trace: tx.id,
          status: tx.status === "completed" ? "Ready" : tx.status === "pending" ? "Pending" : "Failed",
          bankFmt: "CSV",
          regulatorFmt: "PDF",
          utr: tx.status === "completed" ? tx.reference : "—"
        }
      })

      const crrakResults = await Promise.all(crrakPromises)
      const validResults = crrakResults.filter(result => result !== undefined)
      setCrrakAuditData(validResults)
    } catch (error) {
      console.error("Failed to fetch CRRAK audit data:", error)
    }
  }

  // Fetch CRRAK data when component mounts or transactions change
  useEffect(() => {
    if (transactions.length > 0) {
      fetchCRRAKAuditData()
    }
  }, [transactions])

  // Use CRRAK audit data if available, otherwise fallback to basic audit filings
  const auditFilings = useMemo(() => {
    if (crrakAuditData.length > 0) {
      return crrakAuditData
    }
    
    return transactions.map((t) => ({
      trace: t.id,
      status: t.status === "completed" ? "Ready" : t.status === "pending" ? "Pending" : "Failed",
      bankFmt: "CSV",
      regulatorFmt: "PDF",
      utr: t.status === "completed" ? t.reference : "—"
    }))
  }, [transactions, crrakAuditData])

  const filtered = auditFilings.filter((f) => {
    const matchesQ = q.trim().length === 0 || f.trace.toLowerCase().includes(q.toLowerCase())
    const matchesStatus = status === "All" || f.status === status
    return matchesQ && matchesStatus
  })
  const pageCount = Math.max(1, Math.ceil(filtered.length / pageSize))
  const pageRows = filtered.slice((page - 1) * pageSize, page * pageSize)

  // Calculate audit stats
  const auditStats = useMemo(() => {
    const ready = auditFilings.filter(f => f.status === "Ready").length
    const pending = auditFilings.filter(f => f.status === "Pending").length
    const failed = auditFilings.filter(f => f.status === "Failed").length
    const total = auditFilings.length
    const complianceRate = total > 0 ? Math.round((ready / total) * 100) : 100
    
    return { ready, pending, failed, total, complianceRate }
  }, [auditFilings])

  const openStory = (trace: string) => {
    setActiveTrace(trace)
    setOpen(true)
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-semibold tracking-tight text-balance">Audit & Filings (CRRAK)</h1>
        <p className="text-sm text-muted-foreground text-pretty">
          Explain & export: decision stories, bank files, and regulator packs
        </p>
      </div>

      <div className="grid gap-4 md:grid-cols-3">
        <Card className="relative overflow-hidden border-white/10 bg-gradient-to-br from-blue-600/20 via-blue-500/10 to-transparent supports-[backdrop-filter]:backdrop-blur-xl shadow-sm ring-1 ring-border/60">
          <div className="pointer-events-none absolute inset-x-0 top-0 h-px bg-primary/20" aria-hidden="true" />
          <div className="absolute inset-0 bg-gradient-to-br from-blue-500/10 to-transparent" />
          <CardContent className="relative p-4">
            <div className="text-sm font-medium text-gray-300">Packs Ready</div>
            <div className="mt-1 text-2xl font-bold text-white">
              {loading ? "Loading..." : auditStats.ready}
            </div>
          </CardContent>
        </Card>

        <Card className="relative overflow-hidden border-white/10 bg-gradient-to-br from-blue-600/20 via-blue-500/10 to-transparent supports-[backdrop-filter]:backdrop-blur-xl shadow-sm ring-1 ring-border/60">
          <div className="pointer-events-none absolute inset-x-0 top-0 h-px bg-primary/20" aria-hidden="true" />
          <div className="absolute inset-0 bg-gradient-to-br from-blue-500/10 to-transparent" />
          <CardContent className="relative p-4">
            <div className="text-sm font-medium text-gray-300">Pending</div>
            <div className="mt-1 text-2xl font-bold text-white">
              {loading ? "Loading..." : auditStats.pending}
            </div>
          </CardContent>
        </Card>

        <Card className="relative overflow-hidden border-white/10 bg-gradient-to-br from-blue-600/20 via-blue-500/10 to-transparent supports-[backdrop-filter]:backdrop-blur-xl shadow-sm ring-1 ring-border/60">
          <div className="pointer-events-none absolute inset-x-0 top-0 h-px bg-primary/20" aria-hidden="true" />
          <div className="absolute inset-0 bg-gradient-to-br from-blue-500/10 to-transparent" />
          <CardContent className="relative p-4">
            <div className="text-sm font-medium text-gray-300">Compliance</div>
            <div className="mt-1 text-2xl font-bold text-white">
              {loading ? "Loading..." : auditStats.complianceRate}
              <span className="text-base font-medium text-gray-400">%</span>
            </div>
          </CardContent>
        </Card>
      </div>

      <Card className="relative overflow-hidden border-white/10 bg-gradient-to-br from-blue-600/20 via-blue-500/10 to-transparent supports-[backdrop-filter]:backdrop-blur-xl shadow-sm ring-1 ring-border/60">
        <div className="pointer-events-none absolute inset-x-0 top-0 h-px bg-primary/20" aria-hidden="true" />
        <div className="absolute inset-0 bg-gradient-to-br from-blue-500/10 to-transparent" />
        <CardHeader className="relative">
          <CardTitle className="text-sm font-medium text-gray-300">Filters</CardTitle>
        </CardHeader>
        <CardContent className="relative">
          <div className="grid gap-3 md:grid-cols-3">
            <div className="md:col-span-2">
              <label htmlFor="search" className="sr-only">
                Search by Trace ID
              </label>
              <Input
                id="search"
                placeholder="Search by Trace ID…"
                value={q}
                onChange={(e) => {
                  setPage(1)
                  setQ(e.target.value)
                }}
                className="rounded-md"
              />
            </div>
            <div>
              <Select
                value={status}
                onValueChange={(v) => {
                  setPage(1)
                  setStatus(v as typeof status)
                }}
              >
                <SelectTrigger className="rounded-md">
                  <SelectValue placeholder="Status" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="All">All Statuses</SelectItem>
                  <SelectItem value="Ready">Ready</SelectItem>
                  <SelectItem value="Pending">Pending</SelectItem>
                  <SelectItem value="Failed">Failed</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
        </CardContent>
      </Card>

      <Card className="relative overflow-hidden border-white/10 bg-gradient-to-br from-blue-600/20 via-blue-500/10 to-transparent supports-[backdrop-filter]:backdrop-blur-xl shadow-sm ring-1 ring-border/60">
        <div className="pointer-events-none absolute inset-x-0 top-0 h-px bg-primary/20" aria-hidden="true" />
        <div className="absolute inset-0 bg-gradient-to-br from-blue-500/10 to-transparent" />
        <CardHeader className="relative">
          <CardTitle className="text-sm font-medium text-gray-300">Filings</CardTitle>
        </CardHeader>
        <CardContent className="relative">
          <Table>
            <TableHeader className="bg-muted/10">
              <TableRow>
                <TableHead>Trace ID</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Audit Pack</TableHead>
                <TableHead>Bank CSV/XML</TableHead>
                <TableHead>Regulator PDF</TableHead>
                <TableHead>Open Story</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {loading ? (
                <TableRow>
                  <TableCell colSpan={6} className="text-center text-slate-400 py-8">
                    Loading audit filings...
                  </TableCell>
                </TableRow>
              ) : error ? (
                <TableRow>
                  <TableCell colSpan={6} className="text-center text-red-400 py-8">
                    Error loading audit filings: {error}
                  </TableCell>
                </TableRow>
              ) : pageRows.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={6} className="text-center text-slate-400 py-8">
                    No audit filings found
                  </TableCell>
                </TableRow>
              ) : (
                pageRows.map((f, idx) => (
                  <TableRow
                    key={f.trace}
                    className={`${idx % 2 === 0 ? "bg-white/5" : ""} hover:bg-primary/10 transition-colors`}
                  >
                    <TableCell className="font-mono text-xs">{f.trace}</TableCell>
                    <TableCell>
                      <Badge
                        variant="outline"
                        className={
                          f.status === "Ready"
                            ? "rounded-md border-success/40 bg-success/15 text-success-foreground"
                            : f.status === "Pending"
                              ? "rounded-md border-warning/40 bg-warning/15 text-warning-foreground"
                              : "rounded-md border-destructive/40 bg-destructive/15 text-destructive-foreground"
                        }
                      >
                        <span className="mr-1 inline-block h-1.5 w-1.5 rounded-full bg-current" aria-hidden="true" />
                        {f.status}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      <Button
                        size="sm"
                        variant="default"
                        className="rounded-md"
                        title="Download Audit Pack"
                        aria-label={`Download audit pack for ${f.trace}`}
                      >
                        <FileDown className="mr-2 h-3 w-3" /> Download
                      </Button>
                    </TableCell>
                    <TableCell>
                      <Button
                        size="sm"
                        variant="outline"
                        className="rounded-md border-border text-foreground hover:bg-secondary/30 bg-transparent"
                        title={`Bank ${f.bankFmt}`}
                        aria-label={`Download bank ${f.bankFmt} for ${f.trace}`}
                      >
                        <FileText className="mr-2 h-3 w-3" /> {f.bankFmt}
                      </Button>
                    </TableCell>
                    <TableCell>
                      <Button
                        size="sm"
                        variant="outline"
                        className="rounded-md border-border text-foreground hover:bg-secondary/30 bg-transparent"
                        title={f.regulatorFmt}
                        aria-label={`Download regulator ${f.regulatorFmt} for ${f.trace}`}
                      >
                        <BookOpen className="mr-2 h-3 w-3" /> {f.regulatorFmt}
                      </Button>
                    </TableCell>
                    <TableCell>
                      <Button
                        size="sm"
                        variant="ghost"
                        className="rounded-md text-muted-foreground hover:text-foreground"
                        onClick={() => openStory(f.trace)}
                        aria-label={`Open story for ${f.trace}`}
                      >
                        Open Story
                      </Button>
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>

          <div className="mt-4 flex items-center justify-between">
            <div className="text-xs text-muted-foreground">
              Showing {(page - 1) * pageSize + 1}-{Math.min(page * pageSize, filtered.length)} of {filtered.length}
            </div>
            <div className="flex items-center gap-2">
              <Button
                size="sm"
                variant="outline"
                className="rounded-md bg-transparent"
                onClick={() => setPage((p) => Math.max(1, p - 1))}
                disabled={page === 1}
                aria-label="Previous page"
              >
                Prev
              </Button>
              <div className="text-xs">
                Page {page} of {pageCount}
              </div>
              <Button
                size="sm"
                variant="outline"
                className="rounded-md bg-transparent"
                onClick={() => setPage((p) => Math.min(pageCount, p + 1))}
                disabled={page === pageCount}
                aria-label="Next page"
              >
                Next
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      <Drawer open={open} onOpenChange={setOpen}>
        <DrawerContent>
          <DrawerHeader>
            <DrawerTitle>Decision Story</DrawerTitle>
            <DrawerDescription>
              Trace {activeTrace ?? ""} • ACC policy decisions, routing, and final recon
            </DrawerDescription>
          </DrawerHeader>
          <div className="grid gap-4 p-6 md:grid-cols-3">
            <section className="space-y-3 md:col-span-2">
              <h3 className="text-sm font-semibold text-slate-300">Timeline</h3>
              <ol className="space-y-2 text-sm">
                <li>
                  <span className="font-mono text-xs">10:20:00</span> — Created
                </li>
                <li>
                  <span className="font-mono text-xs">10:20:10</span> — ACC decision: Approved (Policy v1.6)
                </li>
                <li>
                  <span className="font-mono text-xs">10:21:20</span> — Routing score-table computed
                </li>
                <li>
                  <span className="font-mono text-xs">10:22:05</span> — Pre-commit re-score
                </li>
                <li>
                  <span className="font-mono text-xs">10:22:15</span> — Dispatch
                </li>
                <li>
                  <span className="font-mono text-xs">10:23:15</span> — UTR received
                </li>
                <li>
                  <span className="font-mono text-xs">10:24:00</span> — Ledger posted & recon final
                </li>
              </ol>

              <div className="grid grid-cols-2 gap-3">
                <div className="rounded-lg border border-white/10 bg-white/5 p-3">
                  <div className="text-xs uppercase text-muted-foreground">ACC Decisions</div>
                  <div className="text-sm">Approved • Policy v1.6</div>
                </div>
                <div className="rounded-lg border border-white/10 bg-white/5 p-3">
                  <div className="text-xs uppercase text-muted-foreground">UTR</div>
                  <div className="font-mono text-xs">UTR2024001230456</div>
                </div>
                <div className="rounded-lg border border-white/10 bg-white/5 p-3">
                  <div className="text-xs uppercase text-muted-foreground">Routing Score-table</div>
                  <div className="text-xs">IMPS: 0.82 • NEFT: 0.71 • RTGS: 0.76</div>
                </div>
                <div className="rounded-lg border border-white/10 bg-white/5 p-3">
                  <div className="text-xs uppercase text-muted-foreground">Re-score Diff</div>
                  <div className="text-xs">IMPS +0.03 post risk-update</div>
                </div>
              </div>

              <div className="rounded-lg border border-white/10 bg-white/5 p-3">
                <div className="text-xs uppercase text-muted-foreground">Ledger entries</div>
                <ul className="text-xs">
                  <li>REQUEST → posted</li>
                  <li>CLEARING → posted</li>
                  <li>SETTLEMENT → posted</li>
                </ul>
              </div>

              <div className="rounded-lg border border-white/10 bg-white/5 p-3">
                <div className="text-xs uppercase text-muted-foreground">Recon final</div>
                <div className="text-sm text-success">Matched</div>
              </div>
            </section>

            <aside className="space-y-3">
              <div className="rounded-lg border border-white/10 bg-white/5 p-3">
                <div className="mb-2 text-xs uppercase text-muted-foreground">Share</div>
                <Button size="sm" variant="outline">
                  <Share2 className="mr-2 h-3 w-3" /> Copy link
                </Button>
                <p className="mt-2 text-xs text-slate-500">Links are time-limited. Watermark “Sandbox” if not prod.</p>
              </div>
              <div className="rounded-lg border border-white/10 bg-white/5 p-3">
                <div className="text-xs uppercase text-muted-foreground">Compliance</div>
                <ul className="text-xs list-disc pl-4">
                  <li>PII masking: ON</li>
                  <li>Idempotency enforced</li>
                  <li>Destructive actions audited</li>
                </ul>
              </div>
            </aside>
          </div>
        </DrawerContent>
      </Drawer>
    </div>
  )
}
