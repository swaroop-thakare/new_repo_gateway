"use client"

import { useState } from "react"
import { Card, CardContent } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Eye, Search } from "lucide-react"
import { TransactionDetailModal } from "@/components/dashboard/transaction-detail-modal"
import { AdvisoryBanner } from "@/components/demo/advisory-banner"

const transactions = [
  {
    id: "12345678",
    date: "2025-09-29",
    beneficiary: "Rajesh Kumar",
    amount: "$45,000",
    status: "completed",
    stage: "reconciled",
    product: "Personal Loan",
    creditScore: 720,
    reference: "UTR2025092912345",
  },
  {
    id: "12345679",
    date: "2025-09-29",
    beneficiary: "Priya Sharma",
    amount: "$32,500",
    status: "pending",
    stage: "operator-review",
    product: "MSME Loan",
    creditScore: 680,
    reference: "L-108",
  },
  {
    id: "12345680",
    date: "2025-09-29",
    beneficiary: "Amit Patel",
    amount: "$78,900",
    status: "completed",
    stage: "executed",
    product: "Business Loan",
    creditScore: 750,
    reference: "UTR2025092912346",
  },
  {
    id: "12345681",
    date: "2025-09-28",
    beneficiary: "Sneha Reddy",
    amount: "$25,000",
    status: "failed",
    stage: "compliance",
    product: "Personal Loan",
    creditScore: 590,
    reference: "L-095",
  },
  {
    id: "12345682",
    date: "2025-09-28",
    beneficiary: "Vikram Singh",
    amount: "$55,000",
    status: "completed",
    stage: "reconciled",
    product: "MSME Loan",
    creditScore: 710,
    reference: "UTR2025092812347",
  },
]

export default function TransactionsPage() {
  const [selectedTransaction, setSelectedTransaction] = useState<string | null>(null)

  const getStatusColor = (status: string) => {
    switch (status) {
      case "completed":
        return "bg-emerald-500/10 text-emerald-500 border-emerald-500/20"
      case "pending":
        return "bg-amber-500/10 text-amber-500 border-amber-500/20"
      case "failed":
        return "bg-red-500/10 text-red-500 border-red-500/20"
      default:
        return "bg-slate-500/10 text-slate-500 border-slate-500/20"
    }
  }

  const getStageColor = (stage: string) => {
    switch (stage) {
      case "reconciled":
        return "bg-emerald-500/10 text-emerald-500 border-emerald-500/20"
      case "executed":
        return "bg-blue-500/10 text-blue-500 border-blue-500/20"
      case "operator-review":
        return "bg-amber-500/10 text-amber-500 border-amber-500/20"
      case "compliance":
        return "bg-purple-500/10 text-purple-500 border-purple-500/20"
      default:
        return "bg-slate-500/10 text-slate-500 border-slate-500/20"
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-white">Transaction Management</h1>
        <p className="text-slate-400 mt-1">View and manage all loan disbursement transactions</p>
      </div>

      {/* Advisories Banner */}
      <AdvisoryBanner className="mt-2" />

      {/* Filters */}
      <Card className="bg-slate-900 border-slate-800">
        <CardContent className="pt-6">
          <div className="grid gap-4 md:grid-cols-4">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400" />
              <Input placeholder="Search transactions..." className="pl-9 bg-slate-800 border-slate-700 text-white" />
            </div>
            <Select>
              <SelectTrigger className="bg-slate-800 border-slate-700 text-white">
                <SelectValue placeholder="Status" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Status</SelectItem>
                <SelectItem value="completed">Completed</SelectItem>
                <SelectItem value="pending">Pending</SelectItem>
                <SelectItem value="failed">Failed</SelectItem>
              </SelectContent>
            </Select>
            <Select>
              <SelectTrigger className="bg-slate-800 border-slate-700 text-white">
                <SelectValue placeholder="Mode" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Modes</SelectItem>
                <SelectItem value="imps">IMPS</SelectItem>
                <SelectItem value="neft">NEFT</SelectItem>
                <SelectItem value="rtgs">RTGS</SelectItem>
              </SelectContent>
            </Select>
            <Select>
              <SelectTrigger className="bg-slate-800 border-slate-700 text-white">
                <SelectValue placeholder="Date Range" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="today">Today</SelectItem>
                <SelectItem value="week">This Week</SelectItem>
                <SelectItem value="month">This Month</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </CardContent>
      </Card>

      {/* Data Grid */}
      <Card className="bg-slate-900 border-slate-800">
        <CardContent className="p-0">
          <Table>
            <TableHeader>
              <TableRow className="border-slate-800 hover:bg-slate-800/50">
                <TableHead className="text-slate-300">Date</TableHead>
                <TableHead className="text-slate-300">Borrower/Beneficiary</TableHead>
                <TableHead className="text-slate-300">Amount</TableHead>
                <TableHead className="text-slate-300">Status</TableHead>
                <TableHead className="text-slate-300">Processing Stage</TableHead>
                <TableHead className="text-slate-300">Loan Product</TableHead>
                <TableHead className="text-slate-300">Credit Score</TableHead>
                <TableHead className="text-slate-300">Reference/UTR</TableHead>
                <TableHead className="text-slate-300">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {transactions.map((transaction) => (
                <TableRow key={transaction.id} className="border-slate-800 hover:bg-slate-800/50">
                  <TableCell className="text-slate-200">{transaction.date}</TableCell>
                  <TableCell className="text-slate-200 font-medium">{transaction.beneficiary}</TableCell>
                  <TableCell className="text-slate-200">{transaction.amount}</TableCell>
                  <TableCell>
                    <Badge variant="outline" className={getStatusColor(transaction.status)}>
                      {transaction.status}
                    </Badge>
                  </TableCell>
                  <TableCell>
                    <Badge variant="outline" className={getStageColor(transaction.stage)}>
                      {transaction.stage}
                    </Badge>
                  </TableCell>
                  <TableCell className="text-slate-200">{transaction.product}</TableCell>
                  <TableCell className="text-slate-200">{transaction.creditScore}</TableCell>
                  <TableCell className="text-slate-200 font-mono text-xs">{transaction.reference}</TableCell>
                  <TableCell>
                    <Button variant="ghost" size="sm" onClick={() => setSelectedTransaction(transaction.id)}>
                      <Eye className="h-4 w-4" />
                    </Button>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>

      <TransactionDetailModal
        transactionId={selectedTransaction}
        open={!!selectedTransaction}
        onClose={() => setSelectedTransaction(null)}
      />
    </div>
  )
}
