"use client"

import React, { useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { AlertCircle, RefreshCw, FileText, XCircle, Download } from "lucide-react"
import { Separator } from "@/components/ui/separator"
import { PageHeader } from "@/components/demo/page-header"
import { useTransactions } from "@/hooks/use-api"

// RCA investigation data interface
interface RCAInvestigationData {
  txnId: string
  remitter: string
  beneficiary: string
  bank: string
  amount: string
  faultParty: "Remitter Bank" | "Beneficiary Bank" | "Network Issue" | "Remitter" | "Beneficiary"
  rootCause: string
  retryable: "YES" | "NO"
  priority: number
  compensationDue: string
  rcaResult?: {
    analysis_id: string
    root_cause: string
    fault_party: string
    retry_eligible: boolean
    priority_score: number
    compensation_amount: number
    evidence_ref: string
  }
}

export default function InvestigationsPage() {
  const { transactions, loading, error } = useTransactions()
  const [rcaData, setRcaData] = useState<RCAInvestigationData[]>([])

  // Filter transactions that need investigation (failed, pending, or in review)
  const investigationTransactions = transactions.filter(t => 
    t.status === "failed" || t.status === "pending" || t.stage === "operator-review"
  )

  const getInvestigationCause = (transaction: any) => {
    if (transaction.status === "failed") {
      return "Rail failure"
    } else if (transaction.stage === "operator-review") {
      return "Manual review required"
    } else if (transaction.stage === "compliance") {
      return "Compliance hold"
    } else if (transaction.status === "pending") {
      return "Pending review"
    }
    return "Unknown issue"
  }

  const getNextStep = (transaction: any) => {
    if (transaction.status === "failed") {
      return "Retry"
    } else if (transaction.stage === "operator-review") {
      return "Review"
    } else if (transaction.stage === "compliance") {
      return "Compliance check"
    } else if (transaction.status === "pending") {
      return "Process"
    }
    return "Investigate"
  }

  const getAssignedTo = (transaction: any) => {
    if (transaction.stage === "operator-review") {
      return "Operations Team"
    } else if (transaction.stage === "compliance") {
      return "Compliance Team"
    } else if (transaction.status === "pending") {
      return "Processing Team"
    }
    return "—"
  }

  // Function to fetch RCA investigation data
  const fetchRCAData = async () => {
    try {
      // Call the RCA service API for real investigation data
      const rcaPromises = investigationTransactions.slice(0, 5).map(async (tx, index) => {
        try {
          const response = await fetch('http://localhost:8009/api/v1/process', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({
              transaction_id: tx.id,
              batch_id: `B-${tx.id}`,
              failure_reason: tx.status === "failed" ? "Transaction failed" : "Pending review"
            })
          })
          
          if (response.ok) {
            const rcaResult = await response.json()
            return {
              txnId: tx.id,
              remitter: `${tx.beneficiary}\nHDFC0001234`,
              beneficiary: `Vendor Ltd\nSBIN0009988`,
              bank: "HDFC Bank",
              amount: `₹${tx.amount.toLocaleString()}`,
              faultParty: rcaResult.fault_party || "Remitter Bank",
              rootCause: typeof rcaResult.root_cause === 'string' ? rcaResult.root_cause : rcaResult.root_cause?.issue || "Insufficient Balance",
              retryable: rcaResult.retry_eligible ? "YES" as const : "NO" as const,
              priority: rcaResult.priority_score || 100,
              compensationDue: rcaResult.compensation_amount > 0 ? `₹${rcaResult.compensation_amount}` : "To Remitter",
              rcaResult: rcaResult
            }
          }
        } catch (error) {
          console.error(`Failed to fetch RCA data for transaction ${tx.id}:`, error)
        }
        
        // Fallback to mock data if RCA service fails
        return {
          txnId: tx.id,
          remitter: tx.beneficiary,
          beneficiary: "Unknown",
          bank: "Unknown",
          amount: `₹${tx.amount.toLocaleString()}`,
          faultParty: "Remitter Bank" as const,
          rootCause: "Unknown issue",
          retryable: "NO" as const,
          priority: 50,
          compensationDue: "To Remitter"
        }
      })
      
      const rcaResults = await Promise.all(rcaPromises)
      const validResults = rcaResults.filter(result => result !== undefined)
      
      if (validResults.length === 0) {
        // Fallback to mock data if no RCA results
        const mockRCAData: RCAInvestigationData[] = [
          {
            txnId: "TXN-2025-006",
            remitter: "Tech Corp\nHDFC0001234",
            beneficiary: "Vendor Ltd\nSBIN0009988",
            bank: "HDFC Bank",
            amount: "₹1,50,000",
            faultParty: "Remitter Bank",
            rootCause: "Insufficient Balance",
            retryable: "NO",
            priority: 100,
            compensationDue: "To Remitter",
            rcaResult: {
              analysis_id: "RCA-2025-006",
              root_cause: "Insufficient Balance",
              fault_party: "Remitter Bank",
              retry_eligible: false,
              priority_score: 100,
              compensation_amount: 0,
              evidence_ref: "s3://arealis-invoices/evidence/RCA-2025-006/analysis.json"
            }
          },
          {
            txnId: "TXN-2025-007",
            remitter: "Pay Services\nSBIN0002345",
            beneficiary: "John Doe\nICIC0004567",
            bank: "SBI",
            amount: "₹75,000",
            faultParty: "Beneficiary Bank",
            rootCause: "Invalid Account",
            retryable: "NO",
            priority: 90,
            compensationDue: "To Beneficiary",
            rcaResult: {
              analysis_id: "RCA-2025-007",
              root_cause: "Invalid Account",
              fault_party: "Beneficiary Bank",
              retry_eligible: false,
              priority_score: 90,
              compensation_amount: 0,
              evidence_ref: "s3://arealis-invoices/evidence/RCA-2025-007/analysis.json"
            }
          },
          {
            txnId: "TXN-2025-008",
            remitter: "Digital Fin\nICIC0003456",
            beneficiary: "Merchant Co\nAXIS0007890",
            bank: "ICICI Bank",
            amount: "₹30,000",
            faultParty: "Network Issue",
            rootCause: "Request Timeout",
            retryable: "YES",
            priority: 80,
            compensationDue: "Both (₹100/day)",
            rcaResult: {
              analysis_id: "RCA-2025-008",
              root_cause: "Request Timeout",
              fault_party: "Network Issue",
              retry_eligible: true,
              priority_score: 80,
              compensation_amount: 100,
              evidence_ref: "s3://arealis-invoices/evidence/RCA-2025-008/analysis.json"
            }
          },
          {
            txnId: "TXN-2025-009",
            remitter: "Smart Pay\nAXIS0004567",
            beneficiary: "Supplier Inc\nHDFC0008901",
            bank: "Axis Bank",
            amount: "₹12,000",
            faultParty: "Remitter Bank",
            rootCause: "Bank System Down",
            retryable: "YES",
            priority: 70,
            compensationDue: "To Remitter",
            rcaResult: {
              analysis_id: "RCA-2025-009",
              root_cause: "Bank System Down",
              fault_party: "Remitter Bank",
              retry_eligible: true,
              priority_score: 70,
              compensation_amount: 0,
              evidence_ref: "s3://arealis-invoices/evidence/RCA-2025-009/analysis.json"
            }
          },
          {
            txnId: "TXN-2025-010",
            remitter: "Wallet Plus\nKKBK0005678",
            beneficiary: "Retailer XYZ\nSBIN0009012",
            bank: "Kotak Bank",
            amount: "₹8,500",
            faultParty: "Beneficiary",
            rootCause: "KYC Incomplete",
            retryable: "NO",
            priority: 60,
            compensationDue: "To Beneficiary",
            rcaResult: {
              analysis_id: "RCA-2025-010",
              root_cause: "KYC Incomplete",
              fault_party: "Beneficiary",
              retry_eligible: false,
              priority_score: 60,
              compensation_amount: 0,
              evidence_ref: "s3://arealis-invoices/evidence/RCA-2025-010/analysis.json"
            }
          }
        ]
        
        setRcaData(mockRCAData)
      } else {
        setRcaData(validResults)
      }
    } catch (error) {
      console.error("Failed to fetch RCA data:", error)
    }
  }

  // Fetch RCA data when component mounts or transactions change
  React.useEffect(() => {
    if (investigationTransactions.length > 0) {
      fetchRCAData()
    }
  }, [investigationTransactions])

  // Calculate Failure Intelligence metrics
  const failedTxns = rcaData.length
  const retryEligible = rcaData.filter(d => d.retryable === "YES").length
  const criticalPriority = rcaData.filter(d => d.priority >= 90).length

  return (
    <div className="space-y-6">
      {/* Gradient PageHeader at the very top for a cohesive overview */}
      <PageHeader eyebrow="Operations" title="Investigations" description="Failure Intelligence & Root Cause Analysis" />
      
      {/* Failure Intelligence Metrics */}
      <div className="grid gap-4 md:grid-cols-3">
        <Card className="glass-card glass-primary">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Failed Txns</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{failedTxns}</div>
            <p className="text-xs text-muted-foreground">Total failed transactions</p>
          </CardContent>
        </Card>
        <Card className="glass-card glass-primary">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Retry-Eligible</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{retryEligible}</div>
            <p className="text-xs text-muted-foreground">Can be retried</p>
          </CardContent>
        </Card>
        <Card className="glass-card glass-primary">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Critical Priority</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{criticalPriority}</div>
            <p className="text-xs text-muted-foreground">High priority issues</p>
          </CardContent>
        </Card>
      </div>
      <Card className="glass-card glass-primary border border-border bg-card/60 supports-[backdrop-filter]:bg-card/50 backdrop-blur bg-gradient-to-b from-sky-500/8 via-cyan-400/5 to-teal-400/8">
        <CardHeader>
          <CardTitle>Failure Intelligence Analysis</CardTitle>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader className="sticky top-0 z-10 bg-card/95 backdrop-blur">
              <TableRow>
                <TableHead>TXN ID</TableHead>
                <TableHead>Remitter</TableHead>
                <TableHead>Beneficiary</TableHead>
                <TableHead>Bank</TableHead>
                <TableHead>Amount (₹)</TableHead>
                <TableHead>Fault Party</TableHead>
                <TableHead>Root Cause</TableHead>
                <TableHead>Retryable</TableHead>
                <TableHead>Priority</TableHead>
                <TableHead>Compensation Due</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {loading ? (
                <TableRow>
                  <TableCell colSpan={10} className="text-center text-slate-400 py-8">
                    Loading RCA analysis...
                  </TableCell>
                </TableRow>
              ) : error ? (
                <TableRow>
                  <TableCell colSpan={10} className="text-center text-red-400 py-8">
                    Error loading RCA data: {error}
                  </TableCell>
                </TableRow>
              ) : rcaData.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={10} className="text-center text-slate-400 py-8">
                    No RCA analysis data available
                  </TableCell>
                </TableRow>
              ) : (
                rcaData.map((data, index) => (
                  <TableRow key={data.txnId} className="hover:bg-muted/40 transition-colors">
                    <TableCell className="font-mono text-sm">{data.txnId}</TableCell>
                    <TableCell className="text-sm">
                      <div className="whitespace-pre-line">{data.remitter}</div>
                    </TableCell>
                    <TableCell className="text-sm">
                      <div className="whitespace-pre-line">{data.beneficiary}</div>
                    </TableCell>
                    <TableCell className="text-sm">{data.bank}</TableCell>
                    <TableCell className="font-medium">{data.amount}</TableCell>
                    <TableCell>
                      <Badge 
                        variant="outline" 
                        className={
                          data.faultParty === "Remitter Bank" ? "bg-red-500/10 text-red-500 border-red-500/20" :
                          data.faultParty === "Beneficiary Bank" ? "bg-orange-500/10 text-orange-500 border-orange-500/20" :
                          data.faultParty === "Network Issue" ? "bg-yellow-500/10 text-yellow-500 border-yellow-500/20" :
                          "bg-blue-500/10 text-blue-500 border-blue-500/20"
                        }
                      >
                        {data.faultParty}
                      </Badge>
                    </TableCell>
                    <TableCell className="text-sm">
                      {typeof data.rootCause === 'string' ? data.rootCause : data.rootCause?.issue || 'Unknown'}
                    </TableCell>
                    <TableCell>
                      <Badge 
                        variant="outline" 
                        className={
                          data.retryable === "YES" ? "bg-emerald-500/10 text-emerald-500 border-emerald-500/20" :
                          "bg-red-500/10 text-red-500 border-red-500/20"
                        }
                      >
                        {data.retryable}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      <Badge 
                        variant="outline" 
                        className={
                          data.priority >= 90 ? "bg-red-500/10 text-red-500 border-red-500/20" :
                          data.priority >= 70 ? "bg-orange-500/10 text-orange-500 border-orange-500/20" :
                          "bg-yellow-500/10 text-yellow-500 border-yellow-500/20"
                        }
                      >
                        {data.priority}
                      </Badge>
                    </TableCell>
                    <TableCell className="text-sm">{data.compensationDue}</TableCell>
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
