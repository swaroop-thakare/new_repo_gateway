"use client"

import { useMemo, useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { ResponsiveContainer, AreaChart, Area, XAxis, YAxis, Tooltip, CartesianGrid, Legend } from "recharts"

type LoanRow = {
  id: string
  borrower: string
  product: "Retail" | "SME" | "Corporate"
  amount: string
  mode: "IMPS" | "NEFT" | "RTGS"
  status: "Approved" | "Pending" | "Failed"
  date: string
}

const LOAN_ROWS: LoanRow[] = [
  {
    id: "LN-20482",
    borrower: "R. Sharma",
    product: "Retail",
    amount: "₹12,50,000",
    mode: "IMPS",
    status: "Approved",
    date: "2025-10-02",
  },
  {
    id: "LN-20479",
    borrower: "A. Verma",
    product: "SME",
    amount: "₹7,80,000",
    mode: "NEFT",
    status: "Pending",
    date: "2025-10-02",
  },
  {
    id: "LN-20475",
    borrower: "T. Nair",
    product: "Corporate",
    amount: "₹3,20,000",
    mode: "RTGS",
    status: "Approved",
    date: "2025-10-01",
  },
  {
    id: "LN-20471",
    borrower: "K. Iyer",
    product: "Retail",
    amount: "₹2,10,000",
    mode: "NEFT",
    status: "Failed",
    date: "2025-10-01",
  },
]

const DAILY = [
  { day: "Mon", amount: 1.1 },
  { day: "Tue", amount: 1.6 },
  { day: "Wed", amount: 1.2 },
  { day: "Thu", amount: 2.0 },
  { day: "Fri", amount: 1.4 },
  { day: "Sat", amount: 0.9 },
  { day: "Sun", amount: 0.7 },
]
const WEEKLY = [
  { day: "W1", amount: 6.8 },
  { day: "W2", amount: 7.2 },
  { day: "W3", amount: 8.1 },
  { day: "W4", amount: 9.0 },
]
const MONTHLY = [
  { day: "Jan", amount: 22.4 },
  { day: "Feb", amount: 24.6 },
  { day: "Mar", amount: 27.1 },
  { day: "Apr", amount: 29.5 },
  { day: "May", amount: 28.2 },
  { day: "Jun", amount: 30.1 },
]

export default function LoanDisbursementsPage() {
  const [query, setQuery] = useState("")
  const [product, setProduct] = useState<"all" | "Retail" | "SME" | "Corporate">("all")
  const [timeframe, setTimeframe] = useState<"daily" | "weekly" | "monthly">("daily")
  const [drawerOpen, setDrawerOpen] = useState(false)

  const chartData = timeframe === "daily" ? DAILY : timeframe === "weekly" ? WEEKLY : MONTHLY

  const filteredRows = useMemo(() => {
    return LOAN_ROWS.filter((r) => {
      const matchQ = query
        ? r.id.toLowerCase().includes(query.toLowerCase()) || r.borrower.toLowerCase().includes(query.toLowerCase())
        : true
      const matchProd = product === "all" ? true : r.product === product
      return matchQ && matchProd
    })
  }, [query, product])

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-semibold">Loan Disbursements</h2>
        <p className="text-slate-600">Batch management for loan disbursements.</p>
      </div>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <Card className="glass-card glass-primary border">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm text-gray-300">Total Disbursed</CardTitle>
          </CardHeader>
          <CardContent className="text-2xl font-bold text-white">₹8.6 Cr</CardContent>
        </Card>
        <Card className="glass-card border">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm text-gray-300">Pending Approvals</CardTitle>
          </CardHeader>
          <CardContent className="text-2xl font-bold text-amber-400">5</CardContent>
        </Card>
        <Card className="glass-card border">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm text-gray-300">Success Rate</CardTitle>
          </CardHeader>
          <CardContent className="text-2xl font-bold text-green-400">97.3%</CardContent>
        </Card>
        <Card className="glass-card border">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm text-gray-300">Avg Time to Disburse</CardTitle>
          </CardHeader>
          <CardContent className="text-2xl font-bold text-white">~42 mins</CardContent>
        </Card>
      </div>

      <div className="flex flex-wrap items-center gap-2">
        <Input
          placeholder="Search loan ID or borrower..."
          className="w-64"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
        />
        <select
          aria-label="Loan type filter"
          className="rounded-md border bg-transparent p-2 text-sm"
          value={product}
          onChange={(e) => setProduct(e.target.value as any)}
        >
          <option value="all">All Types</option>
          <option value="Retail">Retail</option>
          <option value="SME">SME</option>
          <option value="Corporate">Corporate</option>
        </select>

        <div className="ml-auto inline-flex gap-1 rounded-md border p-1">
          <Button variant={timeframe === "daily" ? "default" : "ghost"} size="sm" onClick={() => setTimeframe("daily")}>
            Daily
          </Button>
          <Button
            variant={timeframe === "weekly" ? "default" : "ghost"}
            size="sm"
            onClick={() => setTimeframe("weekly")}
          >
            Weekly
          </Button>
          <Button
            variant={timeframe === "monthly" ? "default" : "ghost"}
            size="sm"
            onClick={() => setTimeframe("monthly")}
          >
            Monthly
          </Button>
        </div>

        <Button variant="outline" size="sm" onClick={() => setDrawerOpen(true)}>
          Approvals & Exceptions
        </Button>
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        <Card className="glass-card glass-primary border lg:col-span-2">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm text-gray-300">Disbursements Over Time</CardTitle>
          </CardHeader>
          <CardContent className="h-[300px]">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={chartData}>
                <defs>
                  <linearGradient id="loanArea" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor="hsl(217 91% 60%)" stopOpacity={0.35} />
                    <stop offset="100%" stopColor="hsl(217 91% 60%)" stopOpacity={0.05} />
                  </linearGradient>
                </defs>
                <CartesianGrid stroke="rgba(255,255,255,0.06)" vertical={false} />
                <XAxis dataKey="day" stroke="rgba(255,255,255,0.6)" />
                <YAxis stroke="rgba(255,255,255,0.6)" />
                <Tooltip
                  contentStyle={{
                    background: "#0f0f0f",
                    border: "1px solid rgba(255,255,255,0.12)",
                    color: "white",
                  }}
                />
                <Legend />
                <Area
                  type="monotone"
                  dataKey="amount"
                  name="Amount (Cr)"
                  stroke="hsl(217 91% 60%)"
                  fill="url(#loanArea)"
                />
              </AreaChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        <Card className="glass-card border">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm text-gray-300">Guidance</CardTitle>
          </CardHeader>
          <CardContent className="text-sm text-gray-300">
            Toggle between Daily / Weekly / Monthly to analyze disbursement velocity. Use Product Type to segment
            cohorts.
          </CardContent>
        </Card>
      </div>

      <Card className="glass-card border">
        <CardHeader className="pb-2">
          <div className="flex items-center justify-between">
            <CardTitle className="text-sm text-gray-300">Recent Disbursements</CardTitle>
            <div className="flex items-center gap-2">
              <Button size="xs" variant="default">
                Export
              </Button>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto rounded-lg border border-white/10">
            <table className="min-w-full text-left text-sm">
              <thead className="bg-white/5 text-gray-300">
                <tr>
                  <th className="px-3 py-2 font-medium">Loan ID</th>
                  <th className="px-3 py-2 font-medium">Borrower</th>
                  <th className="px-3 py-2 font-medium">Product Type</th>
                  <th className="px-3 py-2 font-medium">Amount</th>
                  <th className="px-3 py-2 font-medium">Mode</th>
                  <th className="px-3 py-2 font-medium">Status</th>
                  <th className="px-3 py-2 font-medium">Date</th>
                  <th className="px-3 py-2 font-medium">Action</th>
                </tr>
              </thead>
              <tbody>
                {filteredRows.map((r, idx) => (
                  <tr key={idx} className="border-t border-white/10 hover:bg-white/5">
                    <td className="px-3 py-2 text-white">{r.id}</td>
                    <td className="px-3 py-2 text-white">{r.borrower}</td>
                    <td className="px-3 py-2 text-gray-300">{r.product}</td>
                    <td className="px-3 py-2 text-white">{r.amount}</td>
                    <td className="px-3 py-2 text-gray-300">{r.mode}</td>
                    <td
                      className={`px-3 py-2 ${r.status === "Approved" ? "text-green-400" : r.status === "Pending" ? "text-yellow-400" : "text-red-400"}`}
                    >
                      {r.status}
                    </td>
                    <td className="px-3 py-2 text-gray-300">{r.date}</td>
                    <td className="px-3 py-2">
                      <div className="flex flex-wrap gap-1">
                        <Button size="xs" variant="default">
                          Approve
                        </Button>
                        <Button size="xs" variant="outline">
                          Retry
                        </Button>
                        <Button size="xs" variant="outline">
                          Export
                        </Button>
                        <Button size="xs" variant="ghost">
                          View Details
                        </Button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <div className="mt-3 text-xs text-gray-400">
            Color coding: green = settled, orange = pending, red = failed.
          </div>
        </CardContent>
      </Card>

      {drawerOpen ? (
        <div className="fixed inset-0 z-50" role="dialog" aria-modal="true" aria-label="Loan Approvals & Exceptions">
          <div className="absolute inset-0 bg-black/40 backdrop-blur-sm" onClick={() => setDrawerOpen(false)} />
          <aside className="absolute right-0 top-0 h-full w-full max-w-md border-l border-white/10 bg-[#0f0f0f] shadow-2xl">
            <div className="flex items-center justify-between border-b border-white/10 p-4">
              <h3 className="text-white text-base font-semibold">Pending Loan Approvals</h3>
              <Button size="sm" variant="outline" onClick={() => setDrawerOpen(false)}>
                Close
              </Button>
            </div>
            <div className="p-4 space-y-6">
              <div>
                <div className="mb-2 text-sm text-gray-300">Waiting approvals</div>
                <ul className="space-y-2">
                  {[
                    { id: "LN-20490", borrower: "S. Kapoor", amount: "₹6,40,000" },
                    { id: "LN-20488", borrower: "D. Joshi", amount: "₹3,10,000" },
                    { id: "LN-20485", borrower: "P. Rao", amount: "₹1,90,000" },
                  ].map((x, i) => (
                    <li key={i} className="flex items-center justify-between rounded-md border border-white/10 p-3">
                      <div className="text-sm text-white">
                        {x.id} <span className="text-gray-400">· {x.borrower}</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <div className="text-sm text-white">{x.amount}</div>
                        <Button size="sm">Approve</Button>
                      </div>
                    </li>
                  ))}
                </ul>
              </div>

              <div>
                <div className="mb-2 text-sm text-gray-300">Exceptions (Failed / Stuck)</div>
                <ul className="space-y-2">
                  {[
                    { id: "LN-20471", reason: "NEFT timeout — retry required" },
                    { id: "LN-20463", reason: "RTGS validation error — KYC mismatch" },
                  ].map((x, i) => (
                    <li key={i} className="rounded-md border border-red-500/30 bg-red-500/10 p-3 text-sm text-red-300">
                      {x.id}: {x.reason}
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          </aside>
        </div>
      ) : null}
    </div>
  )
}
