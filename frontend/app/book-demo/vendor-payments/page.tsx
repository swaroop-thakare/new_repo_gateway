"use client"

import { useMemo, useState, useEffect } from "react"
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
import { fetchVendorPayments, formatCurrency, type VendorPaymentData } from "@/lib/api"

const PIE_COLORS = ["#22c55e", "#38bdf8", "#f59e0b", "#f43f5e", "#8b5cf6"]

type Row = {
  vendor: string
  invoiceId: string
  amount: string
  mode: "NEFT" | "UPI" | "IMPS" | "RTGS"
  status: "Paid" | "Pending" | "Failed"
  date: string
  acc_status: string
  decision_reason: string
}

export default function VendorPaymentsPage() {
  const [query, setQuery] = useState("")
  const [status, setStatus] = useState<"all" | "paid" | "pending" | "failed">("all")
  const [mode, setMode] = useState<"all" | "NEFT" | "UPI" | "IMPS" | "RTGS">("all")
  const [range, setRange] = useState<"week" | "month" | "custom">("week")
  const [drawerOpen, setDrawerOpen] = useState(false)
  const [vendorData, setVendorData] = useState<VendorPaymentData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [processingActions, setProcessingActions] = useState<Set<string>>(new Set())

  // Button handler functions
  const handleApprove = async (invoiceId: string, vendor: string) => {
    const actionKey = `approve-${invoiceId}`
    setProcessingActions(prev => new Set(prev).add(actionKey))
    
    console.log(`✅ Approving invoice ${invoiceId} for vendor ${vendor}`)
    
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    alert(`Invoice ${invoiceId} for ${vendor} has been approved!`)
    setProcessingActions(prev => {
      const newSet = new Set(prev)
      newSet.delete(actionKey)
      return newSet
    })
  }

  const handleRetry = async (invoiceId: string, vendor: string) => {
    const actionKey = `retry-${invoiceId}`
    setProcessingActions(prev => new Set(prev).add(actionKey))
    
    console.log(`🔄 Retrying invoice ${invoiceId} for vendor ${vendor}`)
    
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 1500))
    
    alert(`Retrying payment for invoice ${invoiceId} (${vendor})...`)
    setProcessingActions(prev => {
      const newSet = new Set(prev)
      newSet.delete(actionKey)
      return newSet
    })
  }

  const handleExport = async (invoiceId: string, vendor: string) => {
    const actionKey = `export-${invoiceId}`
    setProcessingActions(prev => new Set(prev).add(actionKey))
    
    console.log(`📤 Exporting invoice ${invoiceId} for vendor ${vendor}`)
    
    // Simulate export process
    await new Promise(resolve => setTimeout(resolve, 800))
    
    alert(`Exporting invoice ${invoiceId} for ${vendor}...`)
    setProcessingActions(prev => {
      const newSet = new Set(prev)
      newSet.delete(actionKey)
      return newSet
    })
  }

  const handleViewHistory = (invoiceId: string, vendor: string) => {
    console.log(`📊 Viewing history for invoice ${invoiceId} (${vendor})`)
    alert(`Opening vendor history for ${vendor} (Invoice: ${invoiceId})...`)
  }

  const handleExportAll = async () => {
    console.log(`📤 Exporting all vendor invoices`)
    const totalInvoices = vendorData?.invoices?.length || 0
    
    // Simulate export process
    await new Promise(resolve => setTimeout(resolve, 2000))
    
    alert(`Exporting all ${totalInvoices} vendor invoices to CSV...`)
  }

  const handleClearAllData = async () => {
    const confirmed = window.confirm(
      "⚠️ WARNING: This will permanently delete ALL vendor payment data from the database.\n\n" +
      "This action cannot be undone. Are you sure you want to continue?"
    )
    
    if (!confirmed) return
    
    try {
      console.log(`🗑️ Clearing all vendor payment data...`)
      
      // Call the clear data API
      const response = await fetch('http://localhost:8000/acc/clear-vendor-data', {
        method: 'DELETE',
        headers: {
          'X-API-Key': 'arealis_api_key_2024',
          'Content-Type': 'application/json',
        },
      })
      
      if (response.ok) {
        alert("✅ All vendor payment data has been cleared successfully!")
        // Refresh the data
        window.location.reload()
      } else {
        alert("❌ Failed to clear data. Please try again.")
      }
    } catch (error) {
      console.error("Error clearing data:", error)
      alert("❌ Error clearing data. Please try again.")
    }
  }

  // Fetch vendor payment data on component mount
  useEffect(() => {
    const loadVendorData = async () => {
      try {
        setLoading(true)
        setError(null)
        const data = await fetchVendorPayments()
        if (data) {
          setVendorData(data)
        } else {
          setError("Failed to load vendor payment data")
        }
      } catch (err) {
        setError("Error loading vendor payment data")
        console.error("Error loading vendor data:", err)
      } finally {
        setLoading(false)
      }
    }

    loadVendorData()
  }, [])

  const filteredRows = useMemo(() => {
    if (!vendorData?.invoices) return []
    
    return vendorData.invoices.filter((r) => {
      const matchQ = query
        ? r.vendor.toLowerCase().includes(query.toLowerCase()) ||
          r.invoice_id.toLowerCase().includes(query.toLowerCase())
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
  }, [query, status, mode, vendorData])

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
          <CardContent className="text-2xl font-bold text-white">
            {loading ? "Loading..." : vendorData ? formatCurrency(vendorData.kpis.total_paid) : "₹0"}
          </CardContent>
        </Card>
        <Card className="glass-card border">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm text-gray-300">Vendors Count</CardTitle>
          </CardHeader>
          <CardContent className="text-2xl font-bold text-white">
            {loading ? "Loading..." : vendorData?.kpis.vendors_count || 0}
          </CardContent>
        </Card>
        <Card className="glass-card border">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm text-gray-300">Pending Approvals</CardTitle>
          </CardHeader>
          <CardContent className="text-2xl font-bold text-amber-400">
            {loading ? "Loading..." : vendorData?.kpis.pending_approvals || 0}
          </CardContent>
        </Card>
        <Card className="glass-card border">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm text-gray-300">Avg Settlement Time</CardTitle>
          </CardHeader>
          <CardContent className="text-2xl font-bold text-white">
            {loading ? "Loading..." : vendorData?.kpis.avg_settlement_time || "T+0 days"}
          </CardContent>
        </Card>
      </div>

      {/* Pass/Fail Breakdown */}
      {vendorData?.pass_fail_breakdown && (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <Card className="glass-card border">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm text-gray-300">Pass Transactions</CardTitle>
            </CardHeader>
            <CardContent className="text-2xl font-bold text-green-400">
              {vendorData.pass_fail_breakdown.pass_count}
            </CardContent>
          </Card>
          <Card className="glass-card border">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm text-gray-300">Fail Transactions</CardTitle>
            </CardHeader>
            <CardContent className="text-2xl font-bold text-red-400">
              {vendorData.pass_fail_breakdown.fail_count}
            </CardContent>
          </Card>
          <Card className="glass-card border">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm text-gray-300">Pass Rate</CardTitle>
            </CardHeader>
            <CardContent className="text-2xl font-bold text-green-400">
              {vendorData.pass_fail_breakdown.pass_percentage}%
            </CardContent>
          </Card>
          <Card className="glass-card border">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm text-gray-300">Fail Rate</CardTitle>
            </CardHeader>
            <CardContent className="text-2xl font-bold text-red-400">
              {vendorData.pass_fail_breakdown.fail_percentage}%
            </CardContent>
          </Card>
        </div>
      )}

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
            {loading ? (
              <div className="flex items-center justify-center h-full">
                <div className="text-gray-400">Loading chart data...</div>
              </div>
            ) : (
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={vendorData?.charts.vendor_bar_data || []}>
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
            )}
          </CardContent>
        </Card>

        <Card className="glass-card border">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm text-gray-300">Top Vendors (Share %)</CardTitle>
          </CardHeader>
          <CardContent className="h-[300px]">
            {loading ? (
              <div className="flex items-center justify-center h-full">
                <div className="text-gray-400">Loading chart data...</div>
              </div>
            ) : (
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie dataKey="value" data={vendorData?.charts.vendor_pie_data || []} innerRadius={50} outerRadius={80} paddingAngle={4}>
                    {(vendorData?.charts.vendor_pie_data || []).map((_, i) => (
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
            )}
          </CardContent>
        </Card>
      </div>

      <Card className="glass-card border">
        <CardHeader className="pb-2">
          <div className="flex items-center justify-between">
            <CardTitle className="text-sm text-gray-300">Vendor Invoices</CardTitle>
            <div className="flex items-center gap-2">
              <Button 
                size="sm" 
                variant="destructive"
                onClick={() => handleClearAllData()}
              >
                Clear All Data
              </Button>
              <Button 
                size="sm" 
                variant="default"
                onClick={() => handleExportAll()}
              >
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
                {loading ? (
                  <tr>
                    <td colSpan={7} className="px-3 py-8 text-center text-gray-400">
                      Loading vendor invoices...
                    </td>
                  </tr>
                ) : error ? (
                  <tr>
                    <td colSpan={7} className="px-3 py-8 text-center text-red-400">
                      Error loading data: {error}
                    </td>
                  </tr>
                ) : filteredRows.length === 0 ? (
                  <tr>
                    <td colSpan={7} className="px-3 py-8 text-center text-gray-400">
                      No vendor payments found
                    </td>
                  </tr>
                ) : (
                  filteredRows.map((r, idx) => (
                    <tr key={idx} className="border-t border-white/10 hover:bg-white/5">
                      <td className="px-3 py-2 text-white">{r.vendor}</td>
                      <td className="px-3 py-2 text-white">{r.invoice_id}</td>
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
                          <div className="text-xs text-gray-300 mb-1 w-full">
                            <strong>ACC Status:</strong> {r.acc_status}
                          </div>
                          <div className="text-xs text-gray-400 mb-2 w-full">
                            <strong>Reason:</strong> {r.decision_reason}
                          </div>
                          <Button 
                            size="sm" 
                            variant="default"
                            onClick={() => handleApprove(r.invoice_id, r.vendor)}
                            disabled={processingActions.has(`approve-${r.invoice_id}`)}
                          >
                            {processingActions.has(`approve-${r.invoice_id}`) ? "Processing..." : "Approve"}
                          </Button>
                          <Button 
                            size="sm" 
                            variant="outline"
                            onClick={() => handleRetry(r.invoice_id, r.vendor)}
                            disabled={processingActions.has(`retry-${r.invoice_id}`)}
                          >
                            {processingActions.has(`retry-${r.invoice_id}`) ? "Retrying..." : "Retry"}
                          </Button>
                          <Button 
                            size="sm" 
                            variant="outline"
                            onClick={() => handleExport(r.invoice_id, r.vendor)}
                            disabled={processingActions.has(`export-${r.invoice_id}`)}
                          >
                            {processingActions.has(`export-${r.invoice_id}`) ? "Exporting..." : "Export"}
                          </Button>
                          <Button 
                            size="sm" 
                            variant="ghost"
                            onClick={() => handleViewHistory(r.invoice_id, r.vendor)}
                          >
                            View Vendor History
                          </Button>
                        </div>
                      </td>
                    </tr>
                  ))
                )}
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
                  {vendorData?.invoices
                    .filter(invoice => invoice.status === "Pending")
                    .slice(0, 3)
                    .map((x, i) => (
                      <li key={i} className="flex items-center justify-between rounded-md border border-white/10 p-3">
                        <div className="text-sm text-white">
                          {x.vendor} <span className="text-gray-400">· {x.invoice_id}</span>
                        </div>
                        <div className="flex items-center gap-2">
                          <div className="text-sm text-white">{x.amount}</div>
                          <Button 
                            size="sm"
                            onClick={() => handleApprove(x.invoice_id, x.vendor)}
                            disabled={processingActions.has(`approve-${x.invoice_id}`)}
                          >
                            {processingActions.has(`approve-${x.invoice_id}`) ? "Processing..." : "Approve"}
                          </Button>
                        </div>
                      </li>
                    )) || (
                    <li className="text-sm text-gray-400 p-3">No pending approvals</li>
                  )}
                </ul>
              </div>

              <div>
                <div className="mb-2 text-sm text-gray-300">Top Vendors (by payout)</div>
                <div className="rounded-md border border-white/10 p-3">
                  <ResponsiveContainer width="100%" height={180}>
                    <PieChart>
                      <Pie dataKey="value" data={vendorData?.charts.vendor_pie_data || []} innerRadius={40} outerRadius={70} paddingAngle={4}>
                        {(vendorData?.charts.vendor_pie_data || []).map((_, i) => (
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
