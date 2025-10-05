"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Checkbox } from "@/components/ui/checkbox"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Input } from "@/components/ui/input"
import { Clock, CheckCircle, XCircle, Search, Filter, TrendingUp, AlertTriangle } from "lucide-react"
import { useState, useMemo } from "react"
import { useTransactions } from "@/hooks/use-api"

const approvals = [
  {
    id: "TRC-2024-001234",
    amount: "₹25,000",
    beneficiary: "Vendor Corp (****4567)",
    urgency: "High",
    deadline: "15m",
    requestedBy: "John Smith",
    status: "expiring",
  },
  {
    id: "TRC-2024-001235",
    amount: "₹50,000",
    beneficiary: "Supplier Ltd (****8901)",
    urgency: "Standard",
    deadline: "2h 30m",
    requestedBy: "Jane Doe",
    status: "pending",
  },
  {
    id: "TRC-2024-001236",
    amount: "₹15,000",
    beneficiary: "Contractor Inc (****2345)",
    urgency: "High",
    deadline: "8m",
    requestedBy: "Bob Wilson",
    status: "expiring",
  },
  {
    id: "TRC-2024-001237",
    amount: "₹75,000",
    beneficiary: "Partner Co (****6789)",
    urgency: "Standard",
    deadline: "4h 15m",
    requestedBy: "Alice Johnson",
    status: "pending",
  },
  {
    id: "TRC-2024-001238",
    amount: "₹32,000",
    beneficiary: "Service Provider (****3456)",
    urgency: "High",
    deadline: "22m",
    requestedBy: "Mike Brown",
    status: "pending",
  },
]

export default function ApprovalsPage() {
  const { transactions, loading, error } = useTransactions()
  const [filterUrgency, setFilterUrgency] = useState<string>("all")
  const [searchQuery, setSearchQuery] = useState("")

  // Generate approval data from transactions
  const approvalData = useMemo(() => {
    return transactions
      .filter(t => t.status === "pending" || t.stage === "operator-review")
      .map((t, index) => ({
        id: t.id,
        amount: `₹${t.amount.toLocaleString()}`,
        beneficiary: `${t.beneficiary} (****${String(t.amount).slice(-4)})`,
        urgency: t.amount > 50000 ? "High" : "Standard",
        deadline: t.amount > 50000 ? "15m" : "2h 30m",
        requestedBy: "System",
        status: t.amount > 50000 ? "expiring" : "pending"
      }))
  }, [transactions])

  const filteredApprovals = approvalData.filter((approval) => {
    const matchesUrgency = filterUrgency === "all" || approval.urgency.toLowerCase() === filterUrgency
    const matchesSearch =
      approval.id.toLowerCase().includes(searchQuery.toLowerCase()) ||
      approval.beneficiary.toLowerCase().includes(searchQuery.toLowerCase())
    return matchesUrgency && matchesSearch
  })

  // Calculate approval stats
  const approvalStats = useMemo(() => {
    const pending = approvalData.length
    const expiring = approvalData.filter(a => a.status === "expiring").length
    const approvedToday = transactions.filter(t => t.status === "completed").length
    const rejectedToday = transactions.filter(t => t.status === "failed").length
    
    return { pending, expiring, approvedToday, rejectedToday }
  }, [approvalData, transactions])

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Approvals</h1>
          <p className="text-gray-400">Human-in-loop management with durable timers</p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" className="gap-2 border-red-500/30 bg-red-500/10 text-red-400 hover:bg-red-500/20">
            <XCircle className="h-4 w-4" />
            Reject Selected
          </Button>
          <Button className="gap-2 bg-gradient-to-r from-green-600 to-green-500 hover:from-green-700 hover:to-green-600">
            <CheckCircle className="h-4 w-4" />
            Approve Selected
          </Button>
        </div>
      </div>

      <div className="grid gap-4 md:grid-cols-4">
        <Card className="relative overflow-hidden border-white/10 bg-gradient-to-br from-blue-600/20 via-blue-500/10 to-transparent backdrop-blur-xl">
          <div className="absolute inset-0 bg-gradient-to-br from-blue-500/10 to-transparent" />
          <CardHeader className="relative pb-3">
            <CardTitle className="text-sm font-medium text-gray-300">Pending</CardTitle>
          </CardHeader>
          <CardContent className="relative">
            <div className="text-3xl font-bold text-white">
              {loading ? "Loading..." : approvalStats.pending}
            </div>
            <p className="mt-1 text-xs text-gray-400">Awaiting action</p>
          </CardContent>
        </Card>

        <Card className="relative overflow-hidden border-white/10 bg-gradient-to-br from-red-600/20 via-red-500/10 to-transparent backdrop-blur-xl">
          <div className="absolute inset-0 bg-gradient-to-br from-red-500/10 to-transparent" />
          <CardHeader className="relative pb-3">
            <CardTitle className="text-sm font-medium text-gray-300">Expiring Soon</CardTitle>
          </CardHeader>
          <CardContent className="relative">
            <div className="flex items-center gap-2">
              <AlertTriangle className="h-6 w-6 text-red-400" />
              <div className="text-3xl font-bold text-red-400">
                {loading ? "Loading..." : approvalStats.expiring}
              </div>
            </div>
            <p className="mt-1 text-xs text-gray-400">Within 30 minutes</p>
          </CardContent>
        </Card>

        <Card className="relative overflow-hidden border-white/10 bg-gradient-to-br from-green-600/20 via-green-500/10 to-transparent backdrop-blur-xl">
          <div className="absolute inset-0 bg-gradient-to-br from-green-500/10 to-transparent" />
          <CardHeader className="relative pb-3">
            <CardTitle className="text-sm font-medium text-gray-300">Approved Today</CardTitle>
          </CardHeader>
          <CardContent className="relative">
            <div className="text-3xl font-bold text-green-400">
              {loading ? "Loading..." : approvalStats.approvedToday}
            </div>
            <p className="mt-1 flex items-center gap-1 text-xs text-green-400">
              <TrendingUp className="h-3 w-3" />
              +12% vs yesterday
            </p>
          </CardContent>
        </Card>

        <Card className="relative overflow-hidden border-white/10 bg-gradient-to-br from-blue-600/20 via-blue-500/10 to-transparent backdrop-blur-xl">
          <div className="absolute inset-0 bg-gradient-to-br from-blue-500/10 to-transparent" />
          <CardHeader className="relative pb-3">
            <CardTitle className="text-sm font-medium text-gray-300">Avg Response Time</CardTitle>
          </CardHeader>
          <CardContent className="relative">
            <div className="text-3xl font-bold text-white">
              4.2<span className="text-xl text-gray-400">min</span>
            </div>
            <p className="mt-1 text-xs text-gray-400">Last 24 hours</p>
          </CardContent>
        </Card>
      </div>

      <div className="flex items-center gap-4">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-gray-400" />
          <Input
            placeholder="Search by Trace ID or Beneficiary..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="border-white/10 bg-white/5 pl-10 text-white placeholder:text-gray-500 focus:border-blue-500/50 focus:ring-blue-500/20"
          />
        </div>
        <div className="flex items-center gap-2">
          <Filter className="h-4 w-4 text-gray-400" />
          <Button
            variant="outline"
            size="sm"
            onClick={() => setFilterUrgency("all")}
            className={`border-white/10 ${filterUrgency === "all" ? "bg-blue-500/20 text-blue-400" : "bg-white/5 text-gray-400"}`}
          >
            All
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={() => setFilterUrgency("high")}
            className={`border-white/10 ${filterUrgency === "high" ? "bg-red-500/20 text-red-400" : "bg-white/5 text-gray-400"}`}
          >
            High Priority
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={() => setFilterUrgency("standard")}
            className={`border-white/10 ${filterUrgency === "standard" ? "bg-blue-500/20 text-blue-400" : "bg-white/5 text-gray-400"}`}
          >
            Standard
          </Button>
        </div>
      </div>

      <Card className="relative overflow-hidden border-white/10 bg-[#0d0d0d]/50 backdrop-blur-xl">
        <CardHeader>
          <CardTitle className="text-white">Pending Approvals</CardTitle>
          <p className="text-sm text-gray-400">{filteredApprovals.length} items requiring attention</p>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow className="border-white/5 hover:bg-transparent">
                <TableHead className="w-12">
                  <Checkbox className="border-white/20" />
                </TableHead>
                <TableHead className="text-gray-400">Trace ID</TableHead>
                <TableHead className="text-gray-400">Amount</TableHead>
                <TableHead className="text-gray-400">Beneficiary</TableHead>
                <TableHead className="text-gray-400">Urgency</TableHead>
                <TableHead className="text-gray-400">Deadline</TableHead>
                <TableHead className="text-gray-400">Requested By</TableHead>
                <TableHead className="text-gray-400">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {loading ? (
                <TableRow>
                  <TableCell colSpan={8} className="text-center text-slate-400 py-8">
                    Loading approvals...
                  </TableCell>
                </TableRow>
              ) : error ? (
                <TableRow>
                  <TableCell colSpan={8} className="text-center text-red-400 py-8">
                    Error loading approvals: {error}
                  </TableCell>
                </TableRow>
              ) : filteredApprovals.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={8} className="text-center text-slate-400 py-8">
                    No pending approvals
                  </TableCell>
                </TableRow>
              ) : (
                filteredApprovals.map((approval) => (
                <TableRow key={approval.id} className="border-white/5 transition-colors hover:bg-white/5">
                  <TableCell>
                    <Checkbox className="border-white/20" />
                  </TableCell>
                  <TableCell className="font-mono text-sm text-blue-400">{approval.id}</TableCell>
                  <TableCell className="font-semibold text-white">{approval.amount}</TableCell>
                  <TableCell className="text-gray-300">{approval.beneficiary}</TableCell>
                  <TableCell>
                    <Badge
                      variant="outline"
                      className={
                        approval.urgency === "High"
                          ? "border-red-500/30 bg-red-500/20 text-red-400"
                          : "border-blue-500/30 bg-blue-500/20 text-blue-400"
                      }
                    >
                      {approval.urgency}
                    </Badge>
                  </TableCell>
                  <TableCell>
                    <div className="flex items-center gap-2">
                      <Clock
                        className={`h-4 w-4 ${
                          approval.status === "expiring" ? "animate-pulse text-red-400" : "text-yellow-400"
                        }`}
                      />
                      <span
                        className={`font-medium ${approval.status === "expiring" ? "text-red-400" : "text-gray-300"}`}
                      >
                        {approval.deadline}
                      </span>
                    </div>
                  </TableCell>
                  <TableCell className="text-gray-300">{approval.requestedBy}</TableCell>
                  <TableCell>
                    <div className="flex gap-2">
                      <Button
                        size="sm"
                        className="bg-gradient-to-r from-green-600 to-green-500 text-white hover:from-green-700 hover:to-green-600"
                      >
                        Approve
                      </Button>
                      <Button
                        size="sm"
                        variant="outline"
                        className="border-red-500/30 bg-red-500/10 text-red-400 hover:bg-red-500/20"
                      >
                        Reject
                      </Button>
                    </div>
                  </TableCell>
                </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  )
}
