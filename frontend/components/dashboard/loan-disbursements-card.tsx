"use client"

import { useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { TrendingUp } from "lucide-react"

type LoanRow = {
  id: string
  borrower: string
  amount: string
  status: "Disbursed" | "Pending" | "Failed"
  date: string
  mode: "IMPS" | "NEFT" | "RTGS"
}

const SAMPLE_ROWS: LoanRow[] = [
  {
    id: "LN-20482",
    borrower: "R. Sharma",
    amount: "₹12,50,000",
    status: "Disbursed",
    date: "2025-10-02",
    mode: "IMPS",
  },
  { id: "LN-20479", borrower: "A. Verma", amount: "₹7,80,000", status: "Pending", date: "2025-10-02", mode: "NEFT" },
  { id: "LN-20475", borrower: "T. Nair", amount: "₹3,20,000", status: "Disbursed", date: "2025-10-01", mode: "RTGS" },
  { id: "LN-20471", borrower: "K. Iyer", amount: "₹2,10,000", status: "Failed", date: "2025-10-01", mode: "NEFT" },
]

export default function LoanDisbursementsCard() {
  const [open, setOpen] = useState(false)

  return (
    <>
      <Card className="glass-card glass-primary border">
        <CardHeader className="flex flex-row items-start justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium text-gray-300">Loan Disbursements</CardTitle>
          <button
            className="text-xs text-blue-300 hover:text-blue-200 underline underline-offset-4"
            onClick={() => setOpen(true)}
            aria-label="View Disbursement Report"
          >
            View Disbursement Report
          </button>
        </CardHeader>
        <CardContent className="space-y-3">
          <div className="space-y-1">
            <div className="text-3xl font-bold text-white">
              ₹8.6<span className="text-2xl text-gray-400"> Cr</span>
              <span className="ml-2 inline-flex items-center gap-1 text-sm text-blue-300">
                <TrendingUp className="h-3 w-3" /> +5.4%
              </span>
            </div>
            <div className="text-xs text-gray-400">disbursed</div>
          </div>

          {/* Sparkline */}
          <svg className="h-12 w-full opacity-80" viewBox="0 0 200 48" fill="none" aria-hidden="true">
            <defs>
              <linearGradient id="loanSparkFill" x1="0" y1="0" x2="0" y2="48">
                <stop offset="0%" stopColor="hsl(217 91% 60%)" stopOpacity="0.25" />
                <stop offset="100%" stopColor="hsl(217 91% 60%)" stopOpacity="0" />
              </linearGradient>
            </defs>
            <path
              d="M0 34 L20 30 L40 28 L60 26 L80 22 L100 20 L120 18 L140 19 L160 17 L180 15 L200 14 L200 48 L0 48 Z"
              fill="url(#loanSparkFill)"
            />
            <path
              d="M0 34 L20 30 L40 28 L60 26 L80 22 L100 20 L120 18 L140 19 L160 17 L180 15 L200 14"
              stroke="hsl(217 91% 60%)"
              strokeWidth="2"
              fill="none"
            />
          </svg>
        </CardContent>
      </Card>

      {/* Simple modal drill-down */}
      {open ? (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm p-4"
          role="dialog"
          aria-modal="true"
          aria-label="Loan Disbursements Report"
        >
          <div className="w-full max-w-3xl rounded-xl border border-white/10 bg-[#0f0f0f] shadow-2xl">
            <div className="flex items-center justify-between border-b border-white/10 p-4">
              <h3 className="text-white text-base font-semibold">Loan Disbursements — Report</h3>
              <button
                className="text-sm text-gray-400 hover:text-white"
                onClick={() => setOpen(false)}
                aria-label="Close"
              >
                Close
              </button>
            </div>
            <div className="p-4">
              <div className="mb-3 flex items-center justify-between">
                <div className="text-sm text-gray-300">Recent Disbursements</div>
                <div className="text-xs text-gray-400">Total rows: {SAMPLE_ROWS.length}</div>
              </div>
              <div className="overflow-x-auto rounded-lg border border-white/10">
                <table className="min-w-full text-left text-sm">
                  <thead className="bg-white/5 text-gray-300">
                    <tr>
                      <th className="px-3 py-2 font-medium">Loan ID</th>
                      <th className="px-3 py-2 font-medium">Borrower</th>
                      <th className="px-3 py-2 font-medium">Amount</th>
                      <th className="px-3 py-2 font-medium">Status</th>
                      <th className="px-3 py-2 font-medium">Disbursed On</th>
                      <th className="px-3 py-2 font-medium">Mode</th>
                    </tr>
                  </thead>
                  <tbody>
                    {SAMPLE_ROWS.map((row, i) => (
                      <tr key={i} className="border-t border-white/10 hover:bg-white/5">
                        <td className="px-3 py-2 text-white">{row.id}</td>
                        <td className="px-3 py-2 text-white">{row.borrower}</td>
                        <td className="px-3 py-2 text-white">{row.amount}</td>
                        <td
                          className={
                            row.status === "Disbursed"
                              ? "px-3 py-2 text-green-400"
                              : row.status === "Pending"
                                ? "px-3 py-2 text-yellow-400"
                                : "px-3 py-2 text-red-400"
                          }
                        >
                          {row.status}
                        </td>
                        <td className="px-3 py-2 text-gray-300">{row.date}</td>
                        <td className="px-3 py-2 text-gray-300">{row.mode}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
              <div className="mt-4 text-xs text-gray-400">
                Tracks approvals, routing, and settlement across IMPS/NEFT/RTGS with success visibility.
              </div>
            </div>
          </div>
        </div>
      ) : null}
    </>
  )
}
