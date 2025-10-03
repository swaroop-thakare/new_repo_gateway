"use client"

import { useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { TrendingUp } from "lucide-react"

type VendorRow = {
  vendor: string
  amount: string
  status: "Settled" | "Pending" | "Failed"
  date: string
  mode: "NEFT" | "UPI" | "IMPS" | "RTGS"
}

const SAMPLE_ROWS: VendorRow[] = [
  { vendor: "Acme Supplies", amount: "₹48,20,000", status: "Settled", date: "2025-10-02", mode: "NEFT" },
  { vendor: "Prime Logistics", amount: "₹17,60,000", status: "Pending", date: "2025-10-02", mode: "IMPS" },
  { vendor: "TechNova Pvt Ltd", amount: "₹9,40,000", status: "Settled", date: "2025-10-01", mode: "UPI" },
  { vendor: "Metro Services", amount: "₹3,30,000", status: "Failed", date: "2025-10-01", mode: "NEFT" },
]

export default function VendorPaymentsCard() {
  const [open, setOpen] = useState(false)

  return (
    <>
      <Card className="glass-card glass-primary border">
        <CardHeader className="flex flex-row items-start justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium text-gray-300">Vendor Payments</CardTitle>
          <button
            className="text-xs text-blue-300 hover:text-blue-200 underline underline-offset-4"
            onClick={() => setOpen(true)}
            aria-label="View Vendor Report"
          >
            View Vendor Report
          </button>
        </CardHeader>
        <CardContent className="space-y-3">
          <div className="space-y-1">
            <div className="text-3xl font-bold text-white">
              ₹2.4<span className="text-2xl text-gray-400"> Cr</span>
              <span className="ml-2 inline-flex items-center gap-1 text-sm text-blue-300">
                <TrendingUp className="h-3 w-3" /> +12%
              </span>
            </div>
            <div className="text-xs text-gray-400">paid this month</div>
          </div>

          {/* Sparkline */}
          <svg className="h-12 w-full opacity-80" viewBox="0 0 200 48" fill="none" aria-hidden="true">
            <defs>
              <linearGradient id="vendorSparkFill" x1="0" y1="0" x2="0" y2="48">
                <stop offset="0%" stopColor="hsl(217 91% 60%)" stopOpacity="0.25" />
                <stop offset="100%" stopColor="hsl(217 91% 60%)" stopOpacity="0" />
              </linearGradient>
            </defs>
            <path
              d="M0 38 L20 34 L40 36 L60 28 L80 26 L100 22 L120 20 L140 22 L160 18 L180 16 L200 14 L200 48 L0 48 Z"
              fill="url(#vendorSparkFill)"
            />
            <path
              d="M0 38 L20 34 L40 36 L60 28 L80 26 L100 22 L120 20 L140 22 L160 18 L180 16 L200 14"
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
          aria-label="Vendor Payments Report"
        >
          <div className="w-full max-w-3xl rounded-xl border border-white/10 bg-[#0f0f0f] shadow-2xl">
            <div className="flex items-center justify-between border-b border-white/10 p-4">
              <h3 className="text-white text-base font-semibold">Vendor Payments — Report</h3>
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
                <div className="text-sm text-gray-300">Top Vendors Paid</div>
                <div className="text-xs text-gray-400">Total rows: {SAMPLE_ROWS.length}</div>
              </div>
              <div className="overflow-x-auto rounded-lg border border-white/10">
                <table className="min-w-full text-left text-sm">
                  <thead className="bg-white/5 text-gray-300">
                    <tr>
                      <th className="px-3 py-2 font-medium">Vendor</th>
                      <th className="px-3 py-2 font-medium">Amount</th>
                      <th className="px-3 py-2 font-medium">Status</th>
                      <th className="px-3 py-2 font-medium">Settlement Date</th>
                      <th className="px-3 py-2 font-medium">Mode</th>
                    </tr>
                  </thead>
                  <tbody>
                    {SAMPLE_ROWS.map((row, i) => (
                      <tr key={i} className="border-t border-white/10 hover:bg-white/5">
                        <td className="px-3 py-2 text-white">{row.vendor}</td>
                        <td className="px-3 py-2 text-white">{row.amount}</td>
                        <td
                          className={
                            row.status === "Settled"
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
                Includes NEFT, UPI, IMPS, RTGS vendor payouts with status and settlement visibility.
              </div>
            </div>
          </div>
        </div>
      ) : null}
    </>
  )
}
