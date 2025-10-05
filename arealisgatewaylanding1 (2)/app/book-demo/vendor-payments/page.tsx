"use client"

import { useMemo, useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  Legend,
  PieChart,
  Pie,
  Cell,
} from "recharts"

const VENDOR_BAR_DATA = [
  { vendor: "Acme", amount: 4820000 },
  { vendor: "PrimeLog", amount: 1760000 },
  { vendor: "TechNova", amount: 940000 },
  { vendor: "Metro", amount: 330000 },
  { vendor: "OmniTrade", amount: 280000 },
  { vendor: "RapidTrans", amount: 240000 },
  { vendor: "GreenWorks", amount: 210000 },
  { vendor: "BluePeak", amount: 195000 },
  { vendor: "SilverEdge", amount: 175000 },
  { vendor: "NovaCraft", amount: 160000 },
]

const TOP_VENDORS_PIE = [
  { name: "Acme", value: 48.2 },
  { name: "PrimeLog", value: 17.6 },
  { name: "TechNova", value: 9.4 },
  { name: "Metro", value: 3.3 },
  { name: "Others", value: 21.5 },
]

const PIE_COLORS = ["#22c55e", "#38bdf8", "#f59e0b", "#f43f5e", "#8b5cf6"]

type Row = {
  vendor: string
  invoiceId: string
  amount: string
  mode: "NEFT" | "UPI" | "IMPS" | "RTGS"
  status: "Paid" | "Pending" | "Failed"
  date: string
}

const ROWS: Row[] = [
  {
    vendor: "Acme Supplies",
    invoiceId: "INV-10021",
    amount: "₹4,820,000",
    mode: "NEFT",
    status: "Paid",
    date: "2025-10-02",
  },
  {
    vendor: "Prime Logistics",
    invoiceId: "INV-10022",
    amount: "₹1,760,000",
    mode: "IMPS",
    status: "Pending",
    date: "2025-10-02",
  },
  {
    vendor: "TechNova Pvt Ltd",
    invoiceId: "INV-10018",
    amount: "₹940,000",
    mode: "UPI",
    status: "Paid",
    date: "2025-10-01",
  },
  {
    vendor: "Metro Services",
    invoiceId: "INV-10017",
    amount: "₹330,000",
    mode: "NEFT",
    status: "Failed",
    date: "2025-10-01",
  },
]

export default function VendorPaymentsPage() {
  const [query, setQuery] = useState("")
  const [status, setStatus] = useState<"all" | "paid" | "pending" | "failed">("all")
  const [mode, setMode] = useState<"all" | "NEFT" | "UPI" | "IMPS" | "RTGS">("all")
  const [range, setRange] = useState<"week" | "month" | "custom">("week")
  const [drawerOpen, setDrawerOpen] = useState(false)

  const filteredRows = useMemo(() => {
    return ROWS.filter((r) => {
      const matchQ = query
        ? r.vendor.toLowerCase().includes(query.toLowerCase()) ||
          r.invoiceId.toLowerCase().includes(query.toLowerCase())
        : true
      const matchS =
        status === "all"
          ? true
          : status === "paid"
            ? r.status === "Paid"
            : status === "pending"
              ? r.status === "Pending"
              : r.status === "Failed"
      const matchM = mode === "all" ? true : r.mode === mode
      return matchQ && matchS && matchM
    })
  }, [query, status, mode])

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-semibold">Vendor Payments</h2>
        <p className="text-slate-600">Batch management for vendor payments.</p>
      </div>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <Card className="glass-card glass-primary border">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm text-gray-300">Total Paid</CardTitle>
          </CardHeader>
          <CardContent className="text-2xl font-bold text-white">₹2.4 Cr</CardContent>
        </Card>
        <Card className="glass-card border">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm text-gray-300">Vendors Count</CardTitle>
          </CardHeader>
          <CardContent className="text-2xl font-bold text-white">20</CardContent>
        </Card>
        <Card className="glass-card border">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm text-gray-300">Pending Approvals</CardTitle>
          </CardHeader>
          <CardContent className="text-2xl font-bold text-amber-400">3</CardContent>
        </Card>
        <Card className="glass-card border">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm text-gray-300">Avg Settlement Time</CardTitle>
          </CardHeader>
          <CardContent className="text-2xl font-bold text-white">T+1.2 days</CardContent>
        </Card>
      </div>

      <div className="flex flex-wrap items-center gap-2">
        <Input
          placeholder="Search vendor or invoice..."
          className="w-64"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
        />
        <select
          aria-label="Status filter"
          className="rounded-md border bg-transparent p-2 text-sm"
          value={status}
          onChange={(e) => setStatus(e.target.value as any)}
        >
          <option value="all">All Status</option>
          <option value="paid">Paid</option>
          <option value="pending">Pending</option>
          <option value="failed">Failed</option>
        </select>
        <select
          aria-label="Mode filter"
          className="rounded-md border bg-transparent p-2 text-sm"
          value={mode}
          onChange={(e) => setMode(e.target.value as any)}
        >
          <option value="all">All Modes</option>
          <option value="NEFT">NEFT</option>
          <option value="UPI">UPI</option>
          <option value="IMPS">IMPS</option>
          <option value="RTGS">RTGS</option>
        </select>

        <div className="ml-auto inline-flex gap-1 rounded-md border p-1">
          <Button variant={range === "week" ? "default" : "ghost"} size="sm" onClick={() => setRange("week")}>
            This Week
          </Button>
          <Button variant={range === "month" ? "default" : "ghost"} size="sm" onClick={() => setRange("month")}>
            This Month
          </Button>
          <Button variant={range === "custom" ? "default" : "ghost"} size="sm" onClick={() => setRange("custom")}>
            Custom
          </Button>
        </div>

        <Button variant="outline" size="sm" onClick={() => setDrawerOpen(true)}>
          Approvals & Top Vendors
        </Button>
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        <Card className="glass-card glass-primary border lg:col-span-2">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm text-gray-300">Payments by Vendor (Top 10)</CardTitle>
          </CardHeader>
          <CardContent className="h-[300px]">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={VENDOR_BAR_DATA}>
                <CartesianGrid stroke="rgba(255,255,255,0.06)" vertical={false} />
                <XAxis dataKey="vendor" stroke="rgba(255,255,255,0.6)" />
                <YAxis stroke="rgba(255,255,255,0.6)" />
                <Tooltip
                  contentStyle={{
                    background: "#0f0f0f",
                    border: "1px solid rgba(255,255,255,0.12)",
                    color: "white",
                  }}
                />
                <Legend />
                <Bar dataKey="amount" name="Amount (₹)" fill="hsl(217 91% 60%)" />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        <Card className="glass-card border">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm text-gray-300">Top Vendors (Share %)</CardTitle>
          </CardHeader>
          <CardContent className="h-[300px]">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie dataKey="value" data={TOP_VENDORS_PIE} innerRadius={50} outerRadius={80} paddingAngle={4}>
                  {TOP_VENDORS_PIE.map((_, i) => (
                    <Cell key={i} fill={PIE_COLORS[i % PIE_COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{
                    background: "#0f0f0f",
                    border: "1px solid rgba(255,255,255,0.12)",
                    color: "white",
                  }}
                />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>

      <Card className="glass-card border">
        <CardHeader className="pb-2">
          <div className="flex items-center justify-between">
            <CardTitle className="text-sm text-gray-300">Vendor Invoices</CardTitle>
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
                  <th className="px-3 py-2 font-medium">Vendor Name</th>
                  <th className="px-3 py-2 font-medium">Invoice ID</th>
                  <th className="px-3 py-2 font-medium">Amount</th>
                  <th className="px-3 py-2 font-medium">Mode</th>
                  <th className="px-3 py-2 font-medium">Status</th>
                  <th className="px-3 py-2 font-medium">Settlement Date</th>
                  <th className="px-3 py-2 font-medium">Action</th>
                </tr>
              </thead>
              <tbody>
                {filteredRows.map((r, idx) => (
                  <tr key={idx} className="border-t border-white/10 hover:bg-white/5">
                    <td className="px-3 py-2 text-white">{r.vendor}</td>
                    <td className="px-3 py-2 text-white">{r.invoiceId}</td>
                    <td className="px-3 py-2 text-white">{r.amount}</td>
                    <td className="px-3 py-2 text-gray-300">{r.mode}</td>
                    <td
                      className={`px-3 py-2 ${r.status === "Paid" ? "text-green-400" : r.status === "Pending" ? "text-yellow-400" : "text-red-400"}`}
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
                          View Vendor History
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
        <div className="fixed inset-0 z-50" role="dialog" aria-modal="true" aria-label="Vendor Approvals & Top Vendors">
          <div className="absolute inset-0 bg-black/40 backdrop-blur-sm" onClick={() => setDrawerOpen(false)} />
          <aside className="absolute right-0 top-0 h-full w-full max-w-md border-l border-white/10 bg-[#0f0f0f] shadow-2xl">
            <div className="flex items-center justify-between border-b border-white/10 p-4">
              <h3 className="text-white text-base font-semibold">Pending Approvals</h3>
              <Button size="sm" variant="outline" onClick={() => setDrawerOpen(false)}>
                Close
              </Button>
            </div>
            <div className="p-4 space-y-6">
              <div>
                <div className="mb-2 text-sm text-gray-300">Invoices waiting approval</div>
                <ul className="space-y-2">
                  {[
                    { vendor: "Prime Logistics", invoice: "INV-10022", amount: "₹1,760,000" },
                    { vendor: "Metro Services", invoice: "INV-10025", amount: "₹420,000" },
                    { vendor: "OmniTrade", invoice: "INV-10027", amount: "₹280,000" },
                  ].map((x, i) => (
                    <li key={i} className="flex items-center justify-between rounded-md border border-white/10 p-3">
                      <div className="text-sm text-white">
                        {x.vendor} <span className="text-gray-400">· {x.invoice}</span>
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
                <div className="mb-2 text-sm text-gray-300">Top Vendors (by payout)</div>
                <div className="rounded-md border border-white/10 p-3">
                  <ResponsiveContainer width="100%" height={180}>
                    <PieChart>
                      <Pie dataKey="value" data={TOP_VENDORS_PIE} innerRadius={40} outerRadius={70} paddingAngle={4}>
                        {TOP_VENDORS_PIE.map((_, i) => (
                          <Cell key={i} fill={PIE_COLORS[i % PIE_COLORS.length]} />
                        ))}
                      </Pie>
                      <Tooltip
                        contentStyle={{
                          background: "#0f0f0f",
                          border: "1px solid rgba(255,255,255,0.12)",
                          color: "white",
                        }}
                      />
                      <Legend />
                    </PieChart>
                  </ResponsiveContainer>
                </div>
              </div>
            </div>
          </aside>
        </div>
      ) : null}
    </div>
  )
}
