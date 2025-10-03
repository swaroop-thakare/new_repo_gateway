"use client"

import { useEffect, useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { DollarSign, FileText, TrendingUp, AlertCircle, CheckCircle2, AlertTriangle, Circle } from "lucide-react"
import { toast } from "sonner"
import { WorkflowStepper } from "@/components/dashboard/workflow-stepper"
import { LoanPortfolioCharts } from "@/components/dashboard/loan-portfolio-charts"

export default function DashboardPage() {
  const [mounted, setMounted] = useState(false)

  useEffect(() => {
    setMounted(true)
    toast.success("New Batch B-2025-09-29-01 received from Client System.")
  }, [])

  if (!mounted) return null

  return (
    <div className="space-y-6">
      {/* KPI Cards */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card className="bg-slate-900 border-slate-800">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-slate-200">Total Disbursed Today</CardTitle>
            <DollarSign className="h-4 w-4 text-emerald-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-white">$8,250,400</div>
          </CardContent>
        </Card>

        <Card className="bg-slate-900 border-slate-800">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-slate-200">Loans Processed</CardTitle>
            <FileText className="h-4 w-4 text-emerald-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-white">210</div>
          </CardContent>
        </Card>

        <Card className="bg-slate-900 border-slate-800">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-slate-200">Transaction Success Rate</CardTitle>
            <TrendingUp className="h-4 w-4 text-emerald-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-white">98.0%</div>
          </CardContent>
        </Card>

        <Card className="bg-slate-900 border-slate-800">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-slate-200">Batches Awaiting Action</CardTitle>
            <AlertCircle className="h-4 w-4 text-amber-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-white">3</div>
          </CardContent>
        </Card>
      </div>

      {/* Live Batch Workflow Visualization */}
      <Card className="bg-slate-900 border-slate-800">
        <CardHeader>
          <CardTitle className="text-white">Live Batch Workflow Visualization</CardTitle>
          <p className="text-sm text-slate-400">Batch B-2025-09-29-01</p>
        </CardHeader>
        <CardContent>
          <WorkflowStepper />
        </CardContent>
      </Card>

      {/* Bottom Three Columns */}
      <div className="grid gap-4 md:grid-cols-3">
        {/* Human-in-the-Loop Actions */}
        <Card className="bg-slate-900 border-slate-800">
          <CardHeader>
            <CardTitle className="text-white text-base">Human-in-the-Loop Actions Required</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2 p-3 bg-slate-800 rounded-lg border border-slate-700">
              <div className="flex items-start gap-2">
                <AlertTriangle className="h-4 w-4 text-amber-500 mt-0.5" />
                <div className="flex-1 space-y-2">
                  <p className="text-sm text-slate-200">
                    <span className="font-semibold">Operator Action:</span> Fix IFSC_TYPO for line L-108 in Batch
                    B-2025-09-29-01.
                  </p>
                  <div className="flex gap-2">
                    <Button size="sm" variant="outline" className="h-7 text-xs bg-transparent">
                      Resolve
                    </Button>
                    <Button size="sm" variant="ghost" className="h-7 text-xs">
                      View
                    </Button>
                  </div>
                </div>
              </div>
            </div>

            <div className="space-y-2 p-3 bg-slate-800 rounded-lg border border-slate-700">
              <div className="flex items-start gap-2">
                <CheckCircle2 className="h-4 w-4 text-emerald-500 mt-0.5" />
                <div className="flex-1 space-y-2">
                  <p className="text-sm text-slate-200">
                    <span className="font-semibold">Admin Action:</span> Approve disbursement for Batch B-2025-09-29-01.
                  </p>
                  <div className="flex gap-2">
                    <Button size="sm" className="h-7 text-xs bg-emerald-600 hover:bg-emerald-700">
                      Approve Batch
                    </Button>
                  </div>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Recent Operational Insights */}
        <Card className="bg-slate-900 border-slate-800">
          <CardHeader>
            <CardTitle className="text-white text-base">Recent Operational Insights (RCA Agent)</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="p-3 bg-slate-800 rounded-lg border border-slate-700">
              <div className="flex items-start gap-2">
                <Circle className="h-3 w-3 text-emerald-500 mt-1 fill-current" />
                <p className="text-sm text-slate-300">
                  High failure rate (RC=503) detected for IMPS@HDFC between 14:30-15:00. PDR agent has automatically
                  deprioritized this route.
                </p>
              </div>
            </div>

            <div className="p-3 bg-slate-800 rounded-lg border border-slate-700">
              <div className="flex items-start gap-2">
                <Circle className="h-3 w-3 text-blue-500 mt-1 fill-current" />
                <p className="text-sm text-slate-300">
                  Credit score verification latency increased by 15% for MSME loans. Investigating third-party API
                  performance.
                </p>
              </div>
            </div>

            <div className="p-3 bg-slate-800 rounded-lg border border-slate-700">
              <div className="flex items-start gap-2">
                <Circle className="h-3 w-3 text-amber-500 mt-1 fill-current" />
                <p className="text-sm text-slate-300">
                  Compliance policy acc-v1.4.2 flagged 3 transactions for manual review due to updated KYC requirements.
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Loan Portfolio Snapshot */}
        <Card className="bg-slate-900 border-slate-800">
          <CardHeader>
            <CardTitle className="text-white text-base">Loan Portfolio Snapshot</CardTitle>
          </CardHeader>
          <CardContent>
            <LoanPortfolioCharts />
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
