"use client"

import React, { useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { RefreshCw, XCircle, Eye } from "lucide-react"
import { PageHeader } from "@/components/demo/page-header"
import { KpiCard } from "@/components/demo/kpi-card"
import { Download } from "lucide-react"
import { AdvisoryBanner } from "@/components/demo/advisory-banner"
import { useTransactions } from "@/hooks/use-api"

// ARL reconciliation data interface
interface ARLReconciliationData {
  txnId: string
  sender: string
  receiver: string
  bank: string
  rail: string
  amount: string
  utrMatch: "MATCHED" | "PENDING" | "FUZZY" | "NO MATCH"
  reconStatus: "Auto-Reconciled" | "Orphan-System" | "Amount Mismatch" | "Processing"
  confidence: string
  sla: "✓" | "✗"
  arlResult?: {
    status: string
    matched: Array<{line_id: string, utr: string}>
    exceptions: Array<any>
    journals: Array<{entry_id: string, debit: string, credit: string, amount: number}>
    evidence_ref: string
  }
}

export default function LiveQueuePage() {
  const [refreshing, setRefreshing] = useState(false)
  const [arlData, setArlData] = useState<ARLReconciliationData[]>([])
  const { transactions, loading, error } = useTransactions()

  const handleRefresh = () => {
    setRefreshing(true)
    // The useTransactions hook will automatically refresh
    setTimeout(() => setRefreshing(false), 1000)
  }

  // Function to fetch ARL reconciliation data
  const fetchARLData = async () => {
    try {
      // Call the ARL service API for real reconciliation data
      const arlPromises = transactions.slice(0, 5).map(async (tx, index) => {
        try {
          const response = await fetch('http://localhost:8008/api/v1/process', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({
              batch_id: `B-${tx.id}`,
              line_id: `L${index + 1}`,
              amount: tx.amount
            })
          })

          if (response.ok) {
            const arlResult = await response.json()
            return {
              txnId: tx.id,
              sender: `${tx.beneficiary}\nHDFC0001234`,
              receiver: `Receiver\nSBIN0005678`,
              bank: "HDFC Bank",
              rail: "UPI",
              amount: `₹${tx.amount.toLocaleString()}`,
              utrMatch: arlResult.status === "RECONCILED" ? "MATCHED" as const : "PENDING" as const,
              reconStatus: arlResult.status === "RECONCILED" ? "Auto-Reconciled" as const : "Processing" as const,
              confidence: arlResult.status === "RECONCILED" ? "100%" : "0%",
              sla: arlResult.status === "RECONCILED" ? "✓" : "✗",
              arlResult: arlResult
            }
          }
        } catch (error) {
          console.error(`Failed to fetch ARL data for transaction ${tx.id}:`, error)
        }

        // Fallback to mock data if ARL service fails
        return {
          txnId: tx.id,
          sender: tx.beneficiary,
          receiver: "Unknown",
          bank: "Unknown",
          rail: "NEFT",
          amount: `₹${tx.amount.toLocaleString()}`,
          utrMatch: "PENDING" as const,
          reconStatus: "Processing" as const,
          confidence: "0%",
          sla: "✗" as const
        }
      })

      const arlResults = await Promise.all(arlPromises)
      const validResults = arlResults.filter(result => result !== undefined)

      if (validResults.length === 0) {
        // Fallback to mock data if no ARL results
        const sampleData = [
          {
            txnId: "TXN-2025-001",
            sender: "ABC Corp\nHDFC0001234",
            receiver: "Raj Kumar\nSBIN0005678",
            bank: "HDFC Bank",
            rail: "UPI",
            amount: "₹15,000",
            utrMatch: "MATCHED" as const,
            reconStatus: "Auto-Reconciled" as const,
            confidence: "100%",
            sla: "✓" as const,
            arlResult: {
              status: "RECONCILED",
              matched: [{line_id: "L001", utr: "IFT20251005001254"}],
              exceptions: [],
              journals: [{entry_id: "J-L001", debit: "Expense:Vendors", credit: "Bank:BOI", amount: 15000}],
              evidence_ref: "s3://arealis-invoices/evidence/B-20251005-001/L001/arl.json"
            }
          },
          {
            txnId: "TXN-2025-002",
            sender: "XYZ Ltd\nSBIN0009876",
            receiver: "Priya Sharma\nICIC0001122",
            bank: "SBI",
            rail: "NEFT",
            amount: "₹50,000",
            utrMatch: "MATCHED" as const,
            reconStatus: "Auto-Reconciled" as const,
            confidence: "100%",
            sla: "✓" as const,
            arlResult: {
              status: "RECONCILED",
              matched: [{line_id: "L002", utr: "IFT20251005001255"}],
              exceptions: [],
              journals: [{entry_id: "J-L002", debit: "Expense:Vendors", credit: "Bank:SBI", amount: 50000}],
              evidence_ref: "s3://arealis-invoices/evidence/B-20251005-001/L002/arl.json"
            }
          },
          {
            txnId: "TXN-2025-003",
            sender: "PQR Fintech\nICIC0002233",
            receiver: "Amit Patel\nHDFC0003344",
            bank: "ICICI Bank",
            rail: "IMPS",
            amount: "₹25,000",
            utrMatch: "PENDING" as const,
            reconStatus: "Orphan-System" as const,
            confidence: "0%",
            sla: "✗" as const,
            arlResult: {
              status: "PENDING",
              matched: [],
              exceptions: ["No matching UTR found"],
              journals: [],
              evidence_ref: "s3://arealis-invoices/evidence/B-20251005-001/L003/arl.json"
            }
          },
          {
            txnId: "TXN-2025-004",
            sender: "Global Traders\nAXIS0004455",
            receiver: "Supplier Co\nSBIN0006677",
            bank: "Axis Bank",
            rail: "RTGS",
            amount: "₹2,00,000",
            utrMatch: "FUZZY" as const,
            reconStatus: "Auto-Reconciled" as const,
            confidence: "85%",
            sla: "✓" as const,
            arlResult: {
              status: "RECONCILED",
              matched: [{line_id: "L004", utr: "IFT20251005001256"}],
              exceptions: [],
              journals: [{entry_id: "J-L004", debit: "Expense:Vendors", credit: "Bank:Axis", amount: 200000}],
              evidence_ref: "s3://arealis-invoices/evidence/B-20251005-001/L004/arl.json"
            }
          },
          {
            txnId: "TXN-2025-005",
            sender: "Digital Pay\nKKBK0005566",
            receiver: "Merchant A\nHDFC0007788",
            bank: "Kotak Bank",
            rail: "UPI",
            amount: "₹5,000",
            utrMatch: "NO MATCH" as const,
            reconStatus: "Amount Mismatch" as const,
            confidence: "0%",
            sla: "✓" as const,
            arlResult: {
              status: "FAILED",
              matched: [],
              exceptions: ["Amount mismatch detected"],
              journals: [],
              evidence_ref: "s3://arealis-invoices/evidence/B-20251005-001/L005/arl.json"
            }
          }
        ]

        setArlData(sampleData)
      } else {
        setArlData(validResults)
      }
    } catch (error) {
      console.error("Failed to fetch ARL data:", error)
    }
  }

  // Fetch ARL data when component mounts or transactions change
  React.useEffect(() => {
    if (transactions.length > 0) {
      fetchARLData()
    }
  }, [transactions])

  // Calculate metrics for the new format based on ARL data
  const totalTransactions = arlData.length
  const autoReconciled = arlData.filter(d => d.reconStatus === "Auto-Reconciled").length
  const successRate = totalTransactions > 0 ? Math.round((autoReconciled / totalTransactions) * 100) : 0

  // Filter transactions for different tabs
  const completedTransactions = transactions.filter(t => t.status === "completed")
  const failedTransactions = transactions.filter(t => t.status === "failed")

  return (
    <div className="space-y-6">
      <PageHeader
        eyebrow="Operations"
        title="Live Queue"
        description="Real-time routing & dispatch visibility"
        actions={
          <div className="flex items-center gap-2">
            <Button variant="outline" size="sm">
              <Download className="h-3 w-3 mr-2" />
              Export CSV
            </Button>
          </div>
        }
      />
      <AdvisoryBanner className="mt-2" />
      <div className="grid gap-4 md:grid-cols-3">
        <KpiCard
          label="Total Transactions"
          value={loading ? "Loading..." : totalTransactions.toString()}
          delta="Real-time"
          trend="flat"
        />
        <KpiCard
          label="Auto-Reconciled"
          value={loading ? "Loading..." : autoReconciled.toString()}
          delta="Automated"
          trend="flat"
        />
        <KpiCard
          label="Success Rate"
          value={loading ? "Loading..." : `${successRate}%`}
          delta="Performance"
          trend="flat"
        />
      </div>

      <Tabs defaultValue="pending" className="w-full">
        <TabsList className="bg-background/60 supports-[backdrop-filter]:bg-background/40 backdrop-blur border rounded-lg bg-gradient-to-r from-sky-500/20 via-blue-500/15 to-cyan-500/20">
          <TabsTrigger value="pending" className="tab-pill">
            Live Queue ({totalTransactions})
          </TabsTrigger>
          <TabsTrigger value="release" className="tab-pill">
            Auto-Reconciled ({autoReconciled})
          </TabsTrigger>
          <TabsTrigger value="dispatched" className="tab-pill">
            Manual Review ({totalTransactions - autoReconciled})
          </TabsTrigger>
        </TabsList>

        <TabsContent value="pending" className="space-y-4">
          <Card className="glass-card glass-primary">
            <CardHeader>
              <CardTitle>Transaction Reconciliation Queue</CardTitle>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>TXN ID</TableHead>
                    <TableHead>Sender (Remitter)</TableHead>
                    <TableHead>Receiver (Beneficiary)</TableHead>
                    <TableHead>Bank</TableHead>
                    <TableHead>Rail</TableHead>
                    <TableHead>Amount (₹)</TableHead>
                    <TableHead>UTR Match</TableHead>
                    <TableHead>Recon Status</TableHead>
                    <TableHead>Confidence</TableHead>
                    <TableHead>SLA</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {loading ? (
                    <TableRow>
                      <TableCell colSpan={10} className="text-center text-slate-400 py-8">
                        Loading transactions...
                      </TableCell>
                    </TableRow>
                  ) : error ? (
                    <TableRow>
                      <TableCell colSpan={10} className="text-center text-red-400 py-8">
                        Error loading transactions: {error}
                      </TableCell>
                    </TableRow>
                  ) : arlData.length === 0 ? (
                    <TableRow>
                      <TableCell colSpan={10} className="text-center text-slate-400 py-8">
                        No ARL reconciliation data available
                      </TableCell>
                    </TableRow>
                  ) : (
                    arlData.map((data, index) => {
                      return (
                        <TableRow key={data.txnId} className="hover:bg-muted/40 transition-colors">
                          <TableCell className="font-mono text-sm">{data.txnId}</TableCell>
                          <TableCell className="text-sm">
                            <div className="whitespace-pre-line">{data.sender}</div>
                          </TableCell>
                          <TableCell className="text-sm">
                            <div className="whitespace-pre-line">{data.receiver}</div>
                          </TableCell>
                          <TableCell className="text-sm">{data.bank}</TableCell>
                          <TableCell>
                            <Badge variant="outline" className="bg-secondary text-secondary-foreground">
                              {data.rail}
                            </Badge>
                          </TableCell>
                          <TableCell className="font-medium">{data.amount}</TableCell>
                          <TableCell>
                            <Badge
                              variant="outline"
                              className={
                                data.utrMatch === "MATCHED" ? "bg-emerald-500/10 text-emerald-500 border-emerald-500/20" :
                                data.utrMatch === "PENDING" ? "bg-amber-500/10 text-amber-500 border-amber-500/20" :
                                data.utrMatch === "FUZZY" ? "bg-blue-500/10 text-blue-500 border-blue-500/20" :
                                "bg-red-500/10 text-red-500 border-red-500/20"
                              }
                            >
                              {data.utrMatch}
                            </Badge>
                          </TableCell>
                          <TableCell>
                            <Badge
                              variant="outline"
                              className={
                                data.reconStatus === "Auto-Reconciled" ? "bg-emerald-500/10 text-emerald-500 border-emerald-500/20" :
                                "bg-amber-500/10 text-amber-500 border-amber-500/20"
                              }
                            >
                              {data.reconStatus}
                            </Badge>
                          </TableCell>
                          <TableCell className="text-sm">{data.confidence}</TableCell>
                          <TableCell className="text-center">{data.sla}</TableCell>
                        </TableRow>
                      )
                    })
                  )}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="release" className="space-y-4">
          <Card className="glass-card glass-primary">
            <CardHeader>
              <CardTitle>Release Queue (Pre-commit Re-score)</CardTitle>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Trace ID</TableHead>
                    <TableHead>Amount</TableHead>
                    <TableHead>Selected Rail</TableHead>
                    <TableHead>Re-score At</TableHead>
                    <TableHead>Shift Possible?</TableHead>
                    <TableHead>Age</TableHead>
                    <TableHead>Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {loading ? (
                    <TableRow>
                      <TableCell colSpan={7} className="text-center text-slate-400 py-8">
                        Loading transactions...
                      </TableCell>
                    </TableRow>
                  ) : error ? (
                    <TableRow>
                      <TableCell colSpan={7} className="text-center text-red-400 py-8">
                        Error loading transactions: {error}
                      </TableCell>
                    </TableRow>
                  ) : completedTransactions.length === 0 ? (
                    <TableRow>
                      <TableCell colSpan={7} className="text-center text-slate-400 py-8">
                        No completed transactions
                      </TableCell>
                    </TableRow>
                  ) : (
                    completedTransactions.map((transaction) => (
                      <TableRow key={transaction.id} className="hover:bg-muted/40 transition-colors">
                        <TableCell className="font-mono text-sm">{transaction.id}</TableCell>
                        <TableCell className="font-medium">${transaction.amount.toLocaleString()}</TableCell>
                        <TableCell>
                          <Badge variant="outline" className="bg-secondary text-secondary-foreground">
                            {transaction.stage}
                          </Badge>
                        </TableCell>
                        <TableCell className="font-mono text-sm">{transaction.date}</TableCell>
                        <TableCell>
                          <Badge
                            variant="outline"
                            className="bg-success/15 text-success-foreground"
                          >
                            Yes
                          </Badge>
                        </TableCell>
                        <TableCell>{transaction.date}</TableCell>
                        <TableCell>
                          <div className="flex gap-2">
                            <Button size="sm" variant="outline">
                              <RefreshCw className="h-3 w-3" />
                            </Button>
                            <Button size="sm" variant="outline">
                              <XCircle className="h-3 w-3" />
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
        </TabsContent>

        <TabsContent value="dispatched" className="space-y-4">
          <Card className="glass-card glass-primary">
            <CardHeader>
              <CardTitle>Dispatched (with UTR or Fail Code)</CardTitle>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Trace ID</TableHead>
                    <TableHead>Amount</TableHead>
                    <TableHead>Rail</TableHead>
                    <TableHead>UTR</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead>Time</TableHead>
                    <TableHead>Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {loading ? (
                    <TableRow>
                      <TableCell colSpan={7} className="text-center text-slate-400 py-8">
                        Loading transactions...
                      </TableCell>
                    </TableRow>
                  ) : error ? (
                    <TableRow>
                      <TableCell colSpan={7} className="text-center text-red-400 py-8">
                        Error loading transactions: {error}
                      </TableCell>
                    </TableRow>
                  ) : failedTransactions.length === 0 ? (
                    <TableRow>
                      <TableCell colSpan={7} className="text-center text-slate-400 py-8">
                        No failed transactions
                      </TableCell>
                    </TableRow>
                  ) : (
                    failedTransactions.map((transaction) => (
                      <TableRow key={transaction.id} className="hover:bg-muted/40 transition-colors">
                        <TableCell className="font-mono text-sm">{transaction.id}</TableCell>
                        <TableCell className="font-medium">${transaction.amount.toLocaleString()}</TableCell>
                        <TableCell>
                          <Badge variant="outline" className="bg-secondary text-secondary-foreground">
                            {transaction.stage}
                          </Badge>
                        </TableCell>
                        <TableCell className="font-mono text-xs">{transaction.reference}</TableCell>
                        <TableCell>
                          <Badge
                            variant="outline"
                            className="bg-red-500/10 text-red-500 border-red-500/20"
                          >
                            {transaction.status}
                          </Badge>
                        </TableCell>
                        <TableCell className="text-sm">{transaction.date}</TableCell>
                        <TableCell>
                          <Button size="sm" variant="ghost">
                            <Eye className="h-4 w-4" />
                          </Button>
                        </TableCell>
                      </TableRow>
                    ))
                  )}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}
