"use client"

import { useMemo, useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Input } from "@/components/ui/input"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Calendar, Download, Copy, Eye, Paperclip, RefreshCcw, ShieldAlert } from "lucide-react"
import { PageHeader } from "@/components/demo/page-header"
import { KpiCard } from "@/components/demo/kpi-card"
import { AdvisoryBanner } from "@/components/demo/advisory-banner"
import { cn } from "@/lib/utils"

type JournalStage = "REQUEST" | "CLEARING" | "SETTLEMENT" | "CANCELLATION"

const journals = [
  {
    id: "JRN-10001",
    trace: "TRC-2024-001210",
    stage: "REQUEST",
    rail: "IMPS",
    account: "Ops-01",
    merchant: "Acme Ltd",
    amount: "₹12,000",
    status: "posted",
    createdAt: "2025-10-02 10:21:10",
  },
  {
    id: "JRN-10002",
    trace: "TRC-2024-001211",
    stage: "CLEARING",
    rail: "NEFT",
    account: "Ops-01",
    merchant: "Volt Inc",
    amount: "₹55,000",
    status: "posted",
    createdAt: "2025-10-02 10:19:07",
  },
  {
    id: "JRN-10003",
    trace: "TRC-2024-001212",
    stage: "SETTLEMENT",
    rail: "RTGS",
    account: "Ops-02",
    merchant: "Globex",
    amount: "₹2,50,000",
    status: "posted",
    createdAt: "2025-10-02 10:11:43",
  },
  {
    id: "JRN-10004",
    trace: "TRC-2024-001213",
    stage: "CANCELLATION",
    rail: "IMPS",
    account: "Ops-02",
    merchant: "Acme Ltd",
    amount: "₹12,000",
    status: "posted",
    createdAt: "2025-10-02 10:09:55",
  },
] as Array<{
  id: string
  trace: string
  stage: JournalStage
  rail: string
  account: string
  merchant: string
  amount: string
  status: "posted" | "pending"
  createdAt: string
}>

const exceptions = [
  {
    id: "EXC-9001",
    trace: "TRC-2024-001228",
    rail: "NEFT",
    reason: "Mismatch amount",
    missing: false,
    createdAt: "2025-10-02 09:50:12",
  },
  {
    id: "EXC-9002",
    trace: "TRC-2024-001231",
    rail: "NEFT",
    reason: "Missing UTR",
    missing: true,
    createdAt: "2025-10-02 09:41:02",
  },
  {
    id: "EXC-9003",
    trace: "TRC-2024-001240",
    rail: "IMPS",
    reason: "Unmatched journal",
    missing: false,
    createdAt: "2025-10-02 09:36:44",
  },
]

export default function LedgerReconPage() {
  const [q, setQ] = useState("")
  const [rail, setRail] = useState<string>("all")
  const [status, setStatus] = useState<string>("all")
  const [account, setAccount] = useState<string>("all")

  const filteredJournals = useMemo(() => {
    return journals.filter((j) => {
      const matchQ = q ? [j.id, j.trace, j.merchant].some((v) => v.toLowerCase().includes(q.toLowerCase())) : true
      const matchRail = rail === "all" ? true : j.rail === rail
      const matchStatus = status === "all" ? true : j.status === status
      const matchAccount = account === "all" ? true : j.account === account
      return matchQ && matchRail && matchStatus && matchAccount
    })
  }, [q, rail, status, account])

  return (
    <div className="space-y-6">
      {/* Replace basic title with PageHeader + export action */}
      <PageHeader
        eyebrow="Finance"
        title="Ledger & Recon"
        description="Finance-grade truth with journals and reconciliation"
        actions={
          <Button variant="outline" size="sm">
            <Download className="h-3 w-3 mr-2" />
            Export
          </Button>
        }
      />
      {/* Add advisories banner under header */}
      <AdvisoryBanner className="mt-2" />
      {/* Refined KPI band */}
      <div className="grid gap-4 md:grid-cols-3">
        <KpiCard label="Posted Today" value="1,204" delta="+3.2% vs 24h" trend="up" />
        <KpiCard label="Exceptions" value="8" delta="Watchlist active" trend="down" />
        <KpiCard label="Match Rate" value="92.4%" delta="+0.4% today" trend="up" />
      </div>

      {/* Filters */}
      <Card className="glass-card glass-primary">
        <CardHeader>
          <CardTitle>Filters</CardTitle>
        </CardHeader>
        <CardContent className="grid gap-4 md:grid-cols-5">
          <div className="col-span-2">
            <Input placeholder="Search Trace / Journal / Merchant" value={q} onChange={(e) => setQ(e.target.value)} />
          </div>
          <div className="flex items-center gap-2">
            <Calendar className="h-4 w-4 text-slate-500" />
            <Input type="date" className="w-full" aria-label="From date" />
          </div>
          <div className="flex items-center gap-2">
            <Calendar className="h-4 w-4 text-slate-500" />
            <Input type="date" className="w-full" aria-label="To date" />
          </div>
          <div className="grid grid-cols-3 gap-2 md:col-span-2">
            <Select value={rail} onValueChange={setRail}>
              <SelectTrigger>
                <SelectValue placeholder="Rail" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Rails</SelectItem>
                <SelectItem value="IMPS">IMPS</SelectItem>
                <SelectItem value="NEFT">NEFT</SelectItem>
                <SelectItem value="RTGS">RTGS</SelectItem>
              </SelectContent>
            </Select>
            <Select value={account} onValueChange={setAccount}>
              <SelectTrigger>
                <SelectValue placeholder="Account" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Accounts</SelectItem>
                <SelectItem value="Ops-01">Ops-01</SelectItem>
                <SelectItem value="Ops-02">Ops-02</SelectItem>
              </SelectContent>
            </Select>
            <Select value={status} onValueChange={setStatus}>
              <SelectTrigger>
                <SelectValue placeholder="Status" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Status</SelectItem>
                <SelectItem value="posted">Posted</SelectItem>
                <SelectItem value="pending">Pending</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </CardContent>
      </Card>

      <Tabs defaultValue="journals">
        {/* Glassy tabs bar */}
        <TabsList className="bg-background/60 supports-[backdrop-filter]:bg-background/40 backdrop-blur border rounded-lg bg-gradient-to-r from-sky-500/20 via-blue-500/15 to-cyan-500/20">
          <TabsTrigger value="journals" className="tab-pill">
            Journals
          </TabsTrigger>
          <TabsTrigger value="recon" className="tab-pill">
            Reconciliation
          </TabsTrigger>
          <TabsTrigger value="resolved" className="tab-pill">
            Resolved
          </TabsTrigger>
          <TabsTrigger value="exceptions" className="tab-pill">
            Exceptions
          </TabsTrigger>
        </TabsList>

        <TabsContent value="journals">
          {/* Journals table card uses glass tone */}
          <Card className="glass-card glass-primary">
            <CardHeader>
              <CardTitle>Journals (REQUEST / CLEARING / SETTLEMENT / CANCELLATION)</CardTitle>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader className="sticky top-0 z-10 bg-card/95 backdrop-blur">
                  <TableRow>
                    <TableHead>Journal ID</TableHead>
                    <TableHead>Trace</TableHead>
                    <TableHead>Stage</TableHead>
                    <TableHead>Rail</TableHead>
                    <TableHead>Account</TableHead>
                    <TableHead>Merchant</TableHead>
                    <TableHead>Amount</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead>Created</TableHead>
                    <TableHead>Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {filteredJournals.map((j) => (
                    // Soft row hover
                    <TableRow key={j.id} className="hover:bg-muted/40 transition-colors">
                      <TableCell className="font-mono text-xs">{j.id}</TableCell>
                      <TableCell className="font-mono text-xs">{j.trace}</TableCell>
                      <TableCell>
                        <Badge variant="outline" className="bg-secondary text-secondary-foreground">
                          {j.stage}
                        </Badge>
                      </TableCell>
                      <TableCell>
                        <Badge variant="outline" className="bg-secondary text-secondary-foreground">
                          {j.rail}
                        </Badge>
                      </TableCell>
                      <TableCell>{j.account}</TableCell>
                      <TableCell>{j.merchant}</TableCell>
                      <TableCell className="font-medium">{j.amount}</TableCell>
                      <TableCell>
                        <Badge
                          variant="outline"
                          className={
                            j.status === "posted"
                              ? "bg-success/15 text-success-foreground"
                              : "bg-muted text-muted-foreground"
                          }
                        >
                          {j.status}
                        </Badge>
                      </TableCell>
                      <TableCell className="text-xs">{j.createdAt}</TableCell>
                      <TableCell>
                        <div className="flex gap-2">
                          <Button size="sm" variant="outline" title="Download journal CSV">
                            <Download className="h-3 w-3" />
                          </Button>
                          <Button size="sm" variant="outline" title="Copy journal ID">
                            <Copy className="h-3 w-3" />
                          </Button>
                          <Button size="sm" variant="outline" title="Open associated trace">
                            <Eye className="h-3 w-3" />
                          </Button>
                        </div>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="recon">
          {/* Recon card uses glass tone */}
          <Card className="glass-card glass-primary">
            <CardHeader>
              <CardTitle>Reconciliation</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid gap-4 md:grid-cols-3">
                <Stat title="Total to match" value="32" tone="default" />
                <Stat title="Matched" value="24" tone="success" />
                <Stat title="Exceptions" value="8" tone="warning" />
              </div>
              <div className="rounded-md border">
                <div className="flex items-center justify-between border-b px-4 py-2">
                  <span className="text-sm text-slate-400">Unmatched items sample</span>
                  <Button variant="outline" size="sm">
                    <RefreshCcw className="mr-2 h-3 w-3" />
                    Re-run matching
                  </Button>
                </div>
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Trace</TableHead>
                      <TableHead>Rail</TableHead>
                      <TableHead>Expected</TableHead>
                      <TableHead>Reported</TableHead>
                      <TableHead>Diff</TableHead>
                      <TableHead>Action</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {[
                      { trace: "TRC-2024-001228", rail: "NEFT", exp: "₹45,000", rep: "—", diff: "Missing UTR" },
                      { trace: "TRC-2024-001231", rail: "NEFT", exp: "₹15,000", rep: "₹14,900", diff: "₹100" },
                    ].map((r) => (
                      // Soft row hover
                      <TableRow key={r.trace} className="hover:bg-muted/40 transition-colors">
                        <TableCell className="font-mono text-xs">{r.trace}</TableCell>
                        <TableCell>
                          <Badge variant="outline" className="bg-secondary text-secondary-foreground">
                            {r.rail}
                          </Badge>
                        </TableCell>
                        <TableCell>{r.exp}</TableCell>
                        <TableCell>{r.rep}</TableCell>
                        <TableCell>
                          <Badge variant="outline" className="bg-warning/15 text-warning-foreground">
                            {r.diff}
                          </Badge>
                        </TableCell>
                        <TableCell>
                          <Button size="sm" variant="outline">
                            Match
                          </Button>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="resolved">
          {/* Resolved card uses glass tone */}
          <Card className="glass-card glass-primary">
            <CardHeader>
              <CardTitle>Resolved (matched)</CardTitle>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader className="sticky top-0 z-10 bg-card/95 backdrop-blur">
                  <TableRow>
                    <TableHead>Trace</TableHead>
                    <TableHead>Rail</TableHead>
                    <TableHead>UTR</TableHead>
                    <TableHead>Matched At</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {[
                    {
                      trace: "TRC-2024-001200",
                      rail: "IMPS",
                      utr: "UTR2024001200001",
                      matchedAt: "2025-10-02 09:22:11",
                    },
                    {
                      trace: "TRC-2024-001201",
                      rail: "RTGS",
                      utr: "UTR2024001200002",
                      matchedAt: "2025-10-02 09:24:19",
                    },
                  ].map((r) => (
                    // Soft row hover
                    <TableRow key={r.trace} className="hover:bg-muted/40 transition-colors">
                      <TableCell className="font-mono text-xs">{r.trace}</TableCell>
                      <TableCell>
                        <Badge variant="outline" className="bg-secondary text-secondary-foreground">
                          {r.rail}
                        </Badge>
                      </TableCell>
                      <TableCell className="font-mono text-xs">{r.utr}</TableCell>
                      <TableCell className="text-xs">{r.matchedAt}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="exceptions">
          {/* Exceptions card uses glass tone + tokenized status colors */}
          <Card className="glass-card glass-primary">
            <CardHeader>
              <CardTitle>Exceptions (unmatched, mismatch, missing UTR)</CardTitle>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader className="sticky top-0 z-10 bg-card/95 backdrop-blur">
                  <TableRow>
                    <TableHead>Exception ID</TableHead>
                    <TableHead>Trace</TableHead>
                    <TableHead>Rail</TableHead>
                    <TableHead>Reason</TableHead>
                    <TableHead>Created</TableHead>
                    <TableHead>Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {exceptions.map((e) => (
                    // Soft row hover
                    <TableRow key={e.id} className="hover:bg-muted/40 transition-colors">
                      <TableCell className="font-mono text-xs">{e.id}</TableCell>
                      <TableCell className="font-mono text-xs">{e.trace}</TableCell>
                      <TableCell>
                        <Badge variant="outline" className="bg-secondary text-secondary-foreground">
                          {e.rail}
                        </Badge>
                      </TableCell>
                      <TableCell>
                        <Badge
                          variant="outline"
                          className={
                            e.missing
                              ? "bg-destructive/15 text-destructive-foreground"
                              : "bg-warning/15 text-warning-foreground"
                          }
                        >
                          {e.reason}
                        </Badge>
                      </TableCell>
                      <TableCell className="text-xs">{e.createdAt}</TableCell>
                      <TableCell>
                        <div className="flex gap-2">
                          <Button size="sm" variant="outline" title="Attach document">
                            <Paperclip className="h-3 w-3" />
                          </Button>
                          <Button size="sm" variant="outline" title="Re-match">
                            <RefreshCcw className="h-3 w-3" />
                          </Button>
                          <Button size="sm" variant="outline" title="Raise dispute">
                            <ShieldAlert className="h-3 w-3" />
                          </Button>
                        </div>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}

function Stat({ title, value, tone }: { title: string; value: string; tone: "default" | "success" | "warning" }) {
  const toneClass = tone === "success" ? "glass-success" : tone === "warning" ? "glass-warning" : "glass-primary"

  return (
    <div className={cn("glass-card p-4", toneClass)}>
      <div className="text-xs uppercase tracking-wide text-muted-foreground">{title}</div>
      <div className="text-2xl font-bold">{value}</div>
    </div>
  )
}
